from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import json
from pydantic import BaseModel

from ..db import get_db
from ..models.orm import BatchRecord, AlertRecord, CaseRecord, AssetRecord, RiskScore, FlagRecord, NegativeSpaceFinding, SupervisorNote, CSEFeatures

router = APIRouter()

@router.get("/overview")
def get_overview(batch_id: str, db: Session = Depends(get_db)):
    cse_count = db.query(func.count(func.distinct(AlertRecord.cse_id))).filter(AlertRecord.batch_id == batch_id).scalar() or 0
    alert_count = db.query(AlertRecord).filter(AlertRecord.batch_id == batch_id).count()
    case_count = db.query(CaseRecord).filter(CaseRecord.batch_id == batch_id).count()
    
    ns_count = db.query(NegativeSpaceFinding).filter(NegativeSpaceFinding.batch_id == batch_id).count()
    
    risk_scores = db.query(RiskScore).filter(RiskScore.batch_id == batch_id).all()
    attention_count = sum(1 for rs in risk_scores if rs.risk_level in ['CRITICAL', 'HIGH'])
    
    risk_dist = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unassessed": 0}
    for rs in risk_scores:
        key = rs.risk_level.lower()
        if key in risk_dist:
            risk_dist[key] += 1
            
    top_risks = []
    for rs in sorted(risk_scores, key=lambda x: x.risk_score, reverse=True)[:5]:
        top_risks.append({
            "cse_id": rs.cse_id,
            "risk_score": rs.risk_score,
            "risk_level": rs.risk_level,
            "primary_reason": rs.primary_reason
        })
        
    sector_dist = {}
    cse_features = db.query(CSEFeatures).filter(CSEFeatures.batch_id == batch_id).all()
    for cf in cse_features:
        sec = cf.sector or "Unknown"
        if sec not in sector_dist:
            sector_dist[sec] = {"sector": sec, "critical": 0, "high": 0, "medium": 0, "low": 0}
        
        rs = next((r for r in risk_scores if r.cse_id == cf.cse_id), None)
        if rs and rs.risk_level.lower() in sector_dist[sec]:
            sector_dist[sec][rs.risk_level.lower()] += 1
            
    return {
        "cse_count": cse_count,
        "total_cses": cse_count,
        "alert_count": alert_count,
        "total_alerts": alert_count,
        "case_count": case_count,
        "total_cases": case_count,
        "entities_requiring_attention": attention_count,
        "negative_space_count": ns_count,
        "negative_space_total": ns_count,
        "risk_distribution": risk_dist,
        "top_risks": top_risks,
        "top_risky_entities": top_risks,
        "sector_breakdown": list(sector_dist.values())
    }

@router.get("/entities")
def get_entities(batch_id: str, sort: str = 'risk_score', filter_risk: str = None, filter_sector: str = None, db: Session = Depends(get_db)):
    risk_scores = db.query(RiskScore).filter(RiskScore.batch_id == batch_id).all()
    features = db.query(CSEFeatures).filter(CSEFeatures.batch_id == batch_id).all()
    
    res = []
    for rs in risk_scores:
        feat = next((f for f in features if f.cse_id == rs.cse_id), None)
        sec = feat.sector if feat else "Unknown"
        
        if filter_risk and rs.risk_level.lower() != filter_risk.lower():
            continue
        if filter_sector and sec.lower() != filter_sector.lower():
            continue
            
        res.append({
            "cse_id": rs.cse_id,
            "risk_score": rs.risk_score,
            "risk_level": rs.risk_level,
            "is_grey": rs.is_grey,
            "sector": sec,
            "primary_reason": rs.primary_reason,
            "flag_count": rs.flag_count,
            "alert_count": feat.alert_count if feat else 0
        })
        
    if sort == 'risk_score':
        res.sort(key=lambda x: (x['is_grey'], -x['risk_score']))
        
    return res

@router.get("/entity/{cse_id}")
def get_entity_dossier(cse_id: str, batch_id: str, db: Session = Depends(get_db)):
    rs = db.query(RiskScore).filter(RiskScore.batch_id == batch_id, RiskScore.cse_id == cse_id).first()
    flags = db.query(FlagRecord).filter(FlagRecord.batch_id == batch_id, FlagRecord.cse_id == cse_id).all()
    neg_space = db.query(NegativeSpaceFinding).filter(NegativeSpaceFinding.batch_id == batch_id, NegativeSpaceFinding.cse_id == cse_id).all()
    feats = db.query(CSEFeatures).filter(CSEFeatures.batch_id == batch_id, CSEFeatures.cse_id == cse_id).first()
    note_rec = db.query(SupervisorNote).filter(SupervisorNote.batch_id == batch_id, SupervisorNote.cse_id == cse_id).order_by(SupervisorNote.id.desc()).first()
    
    if not rs:
        return {"error": "Entity not found"}
        
    sec = feats.sector if feats else "Unknown"
    peer_feats = db.query(CSEFeatures).filter(CSEFeatures.batch_id == batch_id, CSEFeatures.sector == sec).all()
    
    metrics_to_compare = ['escalation_rate', 'mean_closure_time_critical', 'critical_asset_telemetry_ratio', 'case_linkage_rate', 'critical_fast_closure_rate']
    peer_context = []
    
    my_feats = json.loads(feats.features_json) if feats else {}
    
    for m in metrics_to_compare:
        vals = []
        for pf in peer_feats:
            f = json.loads(pf.features_json)
            vals.append(f.get(m, 0.0))
        import numpy as np
        if vals:
            peer_context.append({
                "metric": m,
                "cse_value": my_feats.get(m, 0.0),
                "peer_mean": float(np.mean(vals)),
                "peer_p10": float(np.percentile(vals, 10)),
                "peer_p90": float(np.percentile(vals, 90))
            })
            
    shap_list = json.loads(rs.shap_values_json) if rs.shap_values_json else []
    
    return {
        "cse_id": cse_id,
        "sector": sec,
        "risk_score": rs.risk_score,
        "risk_level": rs.risk_level,
        "score_breakdown": json.loads(rs.score_breakdown_json) if rs.score_breakdown_json else {},
        "shap_values": shap_list,
        "feature_contributions": {item["feature"]: item["contribution"] for item in shap_list},
        "flags": [{"rule_id": f.rule_id, "rule_name": f.rule_name, "severity": f.severity, "description": f.description, "evidence_ids": json.loads(f.evidence_ids_json) if f.evidence_ids_json else [], "evidence": json.loads(f.evidence_ids_json) if f.evidence_ids_json else []} for f in flags],
        "negative_space_findings": [{"type": ns.finding_type, "finding_type": ns.finding_type, "severity": ns.severity, "description": ns.description, "expected": ns.expected_value, "observed": ns.observed_value} for ns in neg_space],
        "negative_space": [{"type": ns.finding_type, "finding_type": ns.finding_type, "severity": ns.severity, "description": ns.description, "expected": ns.expected_value, "observed": ns.observed_value} for ns in neg_space],
        "peer_context": peer_context,
        "features": my_feats,
        "supervisor_note": note_rec.note if note_rec else ""
    }

@router.get("/negative-space")
def get_negative_space(batch_id: str, db: Session = Depends(get_db)):
    ns = db.query(NegativeSpaceFinding).filter(NegativeSpaceFinding.batch_id == batch_id).all()
    
    def sev_val(s):
        return {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(s, 0)
        
    res = []
    for n in ns:
        pc_raw = json.loads(n.peer_context_json) if n.peer_context_json else None
        if isinstance(pc_raw, dict) and "peer_mean" in pc_raw:
            pc_str = f"Sector benchmark: {pc_raw['peer_mean']:.1f} avg across {pc_raw.get('peer_count', 0)} peer CSEs"
        elif pc_raw:
            pc_str = str(pc_raw)
        else:
            pc_str = None

        res.append({
            "id": n.id,
            "cse_id": n.cse_id,
            "finding_type": n.finding_type,
            "severity": n.severity,
            "description": n.description,
            "expected": n.expected_value,
            "observed": n.observed_value,
            "asset_id": n.asset_id,
            "peer_context": pc_str,
            "sev_val": sev_val(n.severity)
        })
        
    res.sort(key=lambda x: (-x['sev_val'], x['cse_id']))
    for r in res:
        del r['sev_val']
        
    return {"findings": res, "total": len(res)}

class NoteReq(BaseModel):
    batch_id: str
    cse_id: str
    note: str

@router.post("/notes")
def add_note(req: NoteReq, db: Session = Depends(get_db)):
    import datetime
    note = SupervisorNote(
        batch_id=req.batch_id,
        cse_id=req.cse_id,
        note=req.note,
        created_at=datetime.datetime.utcnow()
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"id": note.id, "created_at": note.created_at}
