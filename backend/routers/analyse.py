from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from datetime import datetime

from ..db import get_db
from ..models.orm import BatchRecord, CSEFeatures, RiskScore, FlagRecord, NegativeSpaceFinding, AlertRecord, CaseRecord, AssetRecord
from ..analytics.feature_engineering import compute_features
from ..analytics.text_similarity import compute_text_similarity
from ..analytics.statistical import compute_z_scores, compute_peer_ranks
from ..analytics.anomaly import run_isolation_forest
from ..analytics.rules import run_rules
from ..analytics.negative_space import detect_negative_space
from ..analytics.risk_score import compute_composite_score, classify_risk
from ..analytics.explainability import compute_attribution

router = APIRouter()

class AnalyseRequest(BaseModel):
    batch_id: str

@router.post("/analyse")
def analyse_batch(req: AnalyseRequest, db: Session = Depends(get_db)):
    batch_id = req.batch_id
    batch = db.query(BatchRecord).filter(BatchRecord.id == batch_id).first()
    if not batch:
        return {"error": "Batch not found"}
        
    cse_ids = json.loads(batch.cse_ids) if batch.cse_ids else []
    
    all_features = {}
    sector_map = {}
    
    # Feature computation
    for cse_id in cse_ids:
        feats = compute_features(cse_id, batch_id, db)
        text_sim = compute_text_similarity(cse_id, batch_id, db)
        feats['investigation_text_similarity'] = text_sim
        
        all_features[cse_id] = feats
        
        # Get sector
        asset = db.query(AssetRecord).filter(AssetRecord.batch_id == batch_id, AssetRecord.cse_id == cse_id, AssetRecord.sector.isnot(None)).first()
        sector_map[cse_id] = asset.sector if asset else "Unknown"
        
        alert_count = db.query(AlertRecord).filter(AlertRecord.batch_id == batch_id, AlertRecord.cse_id == cse_id).count()
        case_count = db.query(CaseRecord).filter(CaseRecord.batch_id == batch_id, CaseRecord.cse_id == cse_id).count()
        
        cse_feat_rec = CSEFeatures(
            batch_id=batch_id,
            cse_id=cse_id,
            features_json=json.dumps(feats),
            sector=sector_map[cse_id],
            alert_count=alert_count,
            case_count=case_count
        )
        db.add(cse_feat_rec)
        
    db.commit()
    
    # Statistical and Anomaly
    z_scores_by_cse = compute_z_scores(all_features)
    peer_ranks_by_cse = compute_peer_ranks(all_features, sector_map)
    anomaly_scores = run_isolation_forest(all_features)
    
    # Orchestrate pipeline per CSE
    for cse_id in cse_ids:
        alert_count = db.query(AlertRecord).filter(AlertRecord.batch_id == batch_id, AlertRecord.cse_id == cse_id).count()
        
        # Update peer features
        all_features[cse_id]['peer_escalation_percentile'] = peer_ranks_by_cse.get(cse_id, {}).get('escalation_rate', 50.0)
        all_features[cse_id]['peer_closure_time_percentile'] = peer_ranks_by_cse.get(cse_id, {}).get('mean_closure_time_critical', 50.0)

        rules_triggered = run_rules(cse_id, all_features[cse_id], batch_id, db, all_features)
        neg_space = detect_negative_space(cse_id, batch_id, db, all_features, sector_map)
        
        score_breakdown, composite = compute_composite_score(
            cse_id, rules_triggered, z_scores_by_cse.get(cse_id, {}),
            peer_ranks_by_cse.get(cse_id, {}), neg_space, alert_count
        )
        
        shap_vals = compute_attribution(all_features[cse_id], score_breakdown)
        risk_level, is_grey, primary_reason = classify_risk(composite, alert_count, rules_triggered, neg_space)
        
        risk_rec = RiskScore(
            batch_id=batch_id,
            cse_id=cse_id,
            risk_score=composite,
            risk_level=risk_level,
            score_breakdown_json=json.dumps(score_breakdown),
            shap_values_json=json.dumps(shap_vals),
            is_grey=is_grey,
            primary_reason=primary_reason,
            flag_count=len(rules_triggered),
            analysed_at=datetime.utcnow()
        )
        db.add(risk_rec)
        
        for rule in rules_triggered:
            flag_rec = FlagRecord(
                batch_id=batch_id,
                cse_id=cse_id,
                rule_id=rule['rule_id'],
                rule_name=rule['rule_name'],
                description=rule['description'],
                severity=rule['severity'],
                flag_type=rule['flag_type'],
                evidence_ids_json=json.dumps(rule.get('evidence_ids', []))
            )
            db.add(flag_rec)
            
        for ns in neg_space:
            ns_rec = NegativeSpaceFinding(
                batch_id=batch_id,
                cse_id=cse_id,
                finding_type=ns['finding_type'],
                asset_id=ns['asset_id'],
                description=ns['description'],
                expected_value=ns['expected_value'],
                observed_value=ns['observed_value'],
                severity=ns['severity'],
                peer_context_json=json.dumps(ns.get('peer_context', {}))
            )
            db.add(ns_rec)
            
    batch.status = 'ANALYSED'
    db.commit()
    
    return {"status": "completed", "entities_processed": len(cse_ids)}
