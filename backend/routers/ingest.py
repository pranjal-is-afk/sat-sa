import os
import uuid
import pandas as pd
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import re

from ..db import get_db
from ..models.orm import BatchRecord, AlertRecord, CaseRecord, AssetRecord

router = APIRouter()

def normalize_severity(sev):
    if pd.isna(sev): return 'INFORMATIONAL'
    sev = str(sev).lower().strip()
    if sev in ['critical', '5', 'p1', 'sev1', 'severity_critical', 'crit']: return 'CRITICAL'
    if sev in ['high', '4', 'p2', 'sev2', 'severity_high']: return 'HIGH'
    if sev in ['medium', '3', 'p3', 'sev3', 'severity_medium', 'med', 'moderate']: return 'MEDIUM'
    if sev in ['low', '2', 'p4', 'sev4', 'severity_low']: return 'LOW'
    return 'INFORMATIONAL'

@router.post("/ingest")
async def ingest_files(
    files: List[UploadFile] = File(...),
    cse_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    batch_id = str(uuid.uuid4())
    
    records_parsed = {'alerts': 0, 'cases': 0, 'assets': 0}
    errors = []
    warnings = []
    all_cse_ids = set()

    if cse_id:
        all_cse_ids.add(cse_id)

    for file in files:
        content = await file.read()
        try:
            content_str = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            errors.append({"file": file.filename, "message": "Failed to decode UTF-8"})
            continue
            
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content_str))
        elif file.filename.endswith('.json'):
            df = pd.read_json(io.StringIO(content_str))
        else:
            warnings.append(f"Skipping {file.filename}: unknown format")
            continue
            
        cols = set(df.columns)
        
        # Determine record type
        is_alert = {'alert_id', 'severity', 'created_at', 'closed_at'}.issubset(cols)
        is_case = {'case_id', 'opened_at'}.issubset(cols)
        is_asset = {'asset_id', 'classification'}.issubset(cols)
        
        if not (is_alert or is_case or is_asset):
            errors.append({"file": file.filename, "message": "Could not determine record type"})
            continue
            
        # Extract CSE ID if missing
        df_cse_id = cse_id
        if not df_cse_id and 'cse_id' not in df.columns:
            match = re.search(r'CSE-\d+', file.filename)
            if match:
                df_cse_id = match.group(0)
                
        if 'cse_id' not in df.columns:
            if df_cse_id:
                df['cse_id'] = df_cse_id
            else:
                errors.append({"file": file.filename, "message": "No cse_id found"})
                continue
                
        all_cse_ids.update(df['cse_id'].dropna().unique())
        
        # Date parsing
        date_cols = ['created_at', 'closed_at', 'acknowledged_at', 'opened_at']
        for dc in date_cols:
            if dc in df.columns:
                df[dc] = pd.to_datetime(df[dc], errors='coerce')
        
        records = df.to_dict('records')
        
        try:
            batch_objects = []
            if is_alert:
                for idx, row in enumerate(records):
                    if pd.isna(row.get('alert_id')) or pd.isna(row.get('created_at')) or pd.isna(row.get('severity')):
                        errors.append({"row": idx, "field": "alert_id/created_at/severity", "message": "Missing required field"})
                        continue
                    
                    closure_mins = None
                    created_val = row.get('created_at')
                    closed_val = row.get('closed_at')
                    ack_val = row.get('acknowledged_at')
                    
                    if not pd.isna(closed_val) and not pd.isna(created_val):
                        closure_mins = (closed_val - created_val).total_seconds() / 60.0
                    
                    created_dt = created_val.to_pydatetime() if isinstance(created_val, pd.Timestamp) else (created_val if not pd.isna(created_val) else None)
                    closed_dt = closed_val.to_pydatetime() if isinstance(closed_val, pd.Timestamp) else (closed_val if not pd.isna(closed_val) else None)
                    ack_dt = ack_val.to_pydatetime() if isinstance(ack_val, pd.Timestamp) else (ack_val if not pd.isna(ack_val) else None)

                    rec = AlertRecord(
                        batch_id=batch_id,
                        alert_id=str(row['alert_id']),
                        cse_id=str(row['cse_id']),
                        severity=normalize_severity(row['severity']),
                        created_at=created_dt,
                        acknowledged_at=ack_dt,
                        closed_at=closed_dt,
                        status=str(row.get('status')) if not pd.isna(row.get('status')) else None,
                        case_id=str(row.get('case_id')) if not pd.isna(row.get('case_id')) else None,
                        asset_id=str(row.get('asset_id')) if not pd.isna(row.get('asset_id')) else None,
                        escalated=bool(row.get('escalated')) if not pd.isna(row.get('escalated')) else None,
                        closure_minutes=closure_mins
                    )
                    batch_objects.append(rec)
                
                if batch_objects:
                    db.add_all(batch_objects)
                    records_parsed['alerts'] += len(batch_objects)
                    
            elif is_case:
                for idx, row in enumerate(records):
                    if pd.isna(row.get('case_id')) or pd.isna(row.get('opened_at')):
                        errors.append({"row": idx, "field": "case_id/opened_at", "message": "Missing required field"})
                        continue
                    
                    opened_val = row.get('opened_at')
                    closed_val = row.get('closed_at')
                    opened_dt = opened_val.to_pydatetime() if isinstance(opened_val, pd.Timestamp) else (opened_val if not pd.isna(opened_val) else None)
                    closed_dt = closed_val.to_pydatetime() if isinstance(closed_val, pd.Timestamp) else (closed_val if not pd.isna(closed_val) else None)

                    rec = CaseRecord(
                        batch_id=batch_id,
                        case_id=str(row['case_id']),
                        cse_id=str(row['cse_id']),
                        opened_at=opened_dt,
                        closed_at=closed_dt,
                        investigation_text=str(row.get('investigation_text')) if not pd.isna(row.get('investigation_text')) else None,
                        investigator_id=str(row.get('investigator_id')) if not pd.isna(row.get('investigator_id')) else None,
                        escalated=bool(row.get('escalated')) if not pd.isna(row.get('escalated')) else None,
                        resolution=str(row.get('resolution')) if not pd.isna(row.get('resolution')) else None,
                        alert_ids=str(row.get('alert_ids')) if not pd.isna(row.get('alert_ids')) else None
                    )
                    batch_objects.append(rec)
                
                if batch_objects:
                    db.add_all(batch_objects)
                    records_parsed['cases'] += len(batch_objects)
                    
            elif is_asset:
                for idx, row in enumerate(records):
                    if pd.isna(row.get('asset_id')) or pd.isna(row.get('classification')):
                        errors.append({"row": idx, "field": "asset_id/classification", "message": "Missing required field"})
                        continue
                        
                    rec = AssetRecord(
                        batch_id=batch_id,
                        asset_id=str(row['asset_id']),
                        cse_id=str(row['cse_id']),
                        classification=str(row['classification']).upper(),
                        asset_type=str(row.get('asset_type')) if not pd.isna(row.get('asset_type')) else None,
                        sector=str(row.get('sector')) if not pd.isna(row.get('sector')) else None
                    )
                    batch_objects.append(rec)
                
                if batch_objects:
                    db.add_all(batch_objects)
                    records_parsed['assets'] += len(batch_objects)
                    
            db.commit()
        except Exception as e:
            db.rollback()
            errors.append({"file": file.filename, "message": str(e)})

    batch = BatchRecord(
        id=batch_id,
        created_at=datetime.utcnow(),
        cse_ids=json.dumps(list(all_cse_ids)),
        status='PENDING'
    )
    db.add(batch)
    db.commit()
    
    return {
        "batch_id": batch_id,
        "records_parsed": records_parsed,
        "errors": errors,
        "warnings": warnings
    }
