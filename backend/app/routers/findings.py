"""
Supervisory Findings & Manual Review Queue Router
Provides filterable findings, prioritized triage queue,
evidence drill-down, and human disposition recording.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3
import json
import uuid
from typing import List, Optional

from backend.app.database.connection import get_db
from backend.app.models.schemas import DispositionRequest
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/findings", tags=["Findings & Review Queue"])

@router.get("")
def list_findings(
    cse_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    query = "SELECT * FROM finding WHERE 1=1"
    params = []

    if cse_id:
        query += " AND cse_id = ?"
        params.append(cse_id)
    if severity:
        query += " AND UPPER(severity) = ?"
        params.append(severity.upper())
    if category:
        query += " AND category = ?"
        params.append(category)
    if status:
        query += " AND UPPER(status) = ?"
        params.append(status.upper())

    query += " ORDER BY priority_score DESC, created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        item = dict(r)
        item["evidence"] = json.loads(item["evidence_json"])
        results.append(item)
    return results

@router.get("/queue")
def get_review_queue(
    limit: int = Query(50),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns top findings prioritized for human manual review."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT f.*, c.name as entity_name, c.sector
        FROM finding f
        JOIN cse c ON f.cse_id = c.cse_id
        WHERE f.status = 'OPEN'
        ORDER BY f.priority_score DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        item = dict(r)
        item["evidence"] = json.loads(item["evidence_json"])
        results.append(item)
    return results

@router.get("/{finding_id}")
def get_finding_detail(finding_id: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM finding WHERE finding_id = ?", (finding_id,))
    f_row = cursor.fetchone()
    if not f_row:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding = dict(f_row)
    finding["evidence"] = json.loads(finding["evidence_json"])

    # Fetch associated records for evidence drill-down
    linked_alert = None
    if finding.get("alert_id"):
        cursor.execute("SELECT * FROM alert WHERE alert_id = ?", (finding["alert_id"],))
        a_row = cursor.fetchone()
        if a_row:
            linked_alert = dict(a_row)

    linked_case = None
    linked_steps = []
    if finding.get("case_id"):
        cursor.execute("SELECT * FROM incident_case WHERE case_id = ?", (finding["case_id"],))
        c_row = cursor.fetchone()
        if c_row:
            linked_case = dict(c_row)
        cursor.execute("SELECT * FROM investigation_step WHERE case_id = ? ORDER BY started_at ASC", (finding["case_id"],))
        linked_steps = [dict(r) for r in cursor.fetchall()]

    linked_asset = None
    if finding.get("asset_id"):
        cursor.execute("SELECT * FROM asset WHERE asset_id = ?", (finding["asset_id"],))
        ass_row = cursor.fetchone()
        if ass_row:
            linked_asset = dict(ass_row)

    # Dispositions
    cursor.execute("SELECT * FROM finding_disposition WHERE finding_id = ? ORDER BY recorded_at DESC", (finding_id,))
    dispositions = [dict(r) for r in cursor.fetchall()]

    # Timeline synthesis
    timeline = []
    if linked_alert and linked_alert.get("created_at"):
        timeline.append({"time": linked_alert["created_at"], "event": "Alert Created by Sensor", "details": f"{linked_alert.get('alert_category')} - {linked_alert.get('severity')}"})
    if linked_alert and linked_alert.get("acknowledged_at"):
        timeline.append({"time": linked_alert["acknowledged_at"], "event": "Analyst Acknowledged Alert", "details": f"Analyst: {linked_alert.get('analyst_id')}"})
    for stp in linked_steps:
        timeline.append({"time": stp.get("started_at"), "event": f"Step: {stp.get('step_name')}", "details": stp.get("notes")})
    if linked_case and linked_case.get("closed_at"):
        timeline.append({"time": linked_case["closed_at"], "event": "Case Marked Closed", "details": f"Reason: {linked_case.get('closure_reason')}"})

    timeline.sort(key=lambda x: str(x.get("time") or ""))

    return {
        "finding": finding,
        "linked_records": {
            "alert": linked_alert,
            "case": linked_case,
            "asset": linked_asset,
            "steps": linked_steps
        },
        "timeline": timeline,
        "dispositions": dispositions
    }

@router.post("/{finding_id}/disposition")
def record_disposition(
    finding_id: str,
    payload: DispositionRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM finding WHERE finding_id = ?", (finding_id,))
    finding = cursor.fetchone()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    disp_id = f"DISP-{uuid.uuid4().hex[:8].upper()}"
    new_status = payload.decision.upper().replace(" ", "_")

    # Update finding status
    cursor.execute("UPDATE finding SET status = ? WHERE finding_id = ?", (new_status, finding_id))
    
    # Record disposition
    cursor.execute("""
        INSERT INTO finding_disposition (disposition_id, finding_id, reviewer_id, decision, comment)
        VALUES (?, ?, ?, ?, ?)
    """, (disp_id, finding_id, payload.reviewer_id, payload.decision, payload.comment))
    db.commit()

    # Log to cryptographic audit trail
    audit_hash = log_audit_event(
        db,
        action="RECORD_SUPERVISORY_DISPOSITION",
        user_id=payload.reviewer_id,
        payload={
            "finding_id": finding_id,
            "disposition_id": disp_id,
            "decision": payload.decision,
            "comment": payload.comment,
            "prior_status": finding["status"],
            "new_status": new_status
        }
    )

    return {
        "finding_id": finding_id,
        "status": new_status,
        "disposition_id": disp_id,
        "audit_hash": audit_hash,
        "message": "Supervisory review disposition recorded and appended to cryptographic audit trail."
    }
