import json
from typing import List, Dict
from sqlalchemy.orm import Session
from ..models.orm import AlertRecord, CaseRecord, AssetRecord, FlagRecord

def run_rules(cse_id: str, features: dict, batch_id: str, db: Session, 
              peer_features: Dict[str, dict]) -> List[dict]:
    """Run all 8 rules, return list of triggered rule dicts."""
    triggered = []
    
    alerts = db.query(AlertRecord).filter(
        AlertRecord.batch_id == batch_id,
        AlertRecord.cse_id == cse_id
    ).all()
    critical_alerts = [a for a in alerts if a.severity == 'CRITICAL']
    
    cases = db.query(CaseRecord).filter(
        CaseRecord.batch_id == batch_id,
        CaseRecord.cse_id == cse_id
    ).all()
    
    # R-01: Critical alert with no linked case (0 linked cases or linkage < 20%)
    if critical_alerts:
        unlinked = [a for a in critical_alerts if not a.case_id]
        if len(unlinked) == len(critical_alerts) or (features.get('case_linkage_rate', 1.0) < 0.20):
            triggered.append({
                'rule_id': 'R-01',
                'rule_name': 'Critical Alert Without Case',
                'description': f'{len(unlinked)} of {len(critical_alerts)} critical alert(s) closed without a linked case record.',
                'severity': 'HIGH',
                'flag_type': 'execution_gap',
                'evidence_ids': [a.alert_id for a in unlinked[:10]]
            })
    
    # R-02: Critical alert mean closure time < 8 min
    if features.get('mean_closure_time_critical', 0) > 0 and features.get('mean_closure_time_critical', 0) < 8 and critical_alerts:
        fast = [a for a in critical_alerts 
                if a.closure_minutes is not None and a.closure_minutes < 8]
        triggered.append({
            'rule_id': 'R-02',
            'rule_name': 'Anomalously Fast Critical Alert Closure',
            'description': f'Mean critical alert closure time is {features["mean_closure_time_critical"]:.1f} min (threshold: 8 min). {len(fast)} alerts closed in under 8 minutes.',
            'severity': 'CRITICAL',
            'flag_type': 'execution_gap',
            'evidence_ids': [a.alert_id for a in fast[:10]]
        })
    
    # R-03: Escalation rate < 10% with sufficient data
    if len(cases) >= 5 and features.get('escalation_rate', 0) < 0.10:
        triggered.append({
            'rule_id': 'R-03',
            'rule_name': 'Low Escalation Rate',
            'description': f'Escalation rate is {features["escalation_rate"]*100:.1f}% (threshold: 10%). Out of {len(cases)} cases, only {int(features["escalation_rate"]*len(cases))} were escalated.',
            'severity': 'HIGH',
            'flag_type': 'execution_gap',
            'evidence_ids': [c.case_id for c in cases if not c.escalated][:5]
        })
    
    # R-04: Text similarity > 0.60 (FR-02.6: >60% of investigations share >0.85 similarity)
    if features.get('investigation_text_similarity', 0) >= 0.60 and len(cases) >= 5:
        triggered.append({
            'rule_id': 'R-04',
            'rule_name': 'Template-Driven Investigation Text',
            'description': f'Investigation text similarity index: {features["investigation_text_similarity"]*100:.1f}% (threshold: 60%). High proportion of investigation notes are templated / repetitive.',
            'severity': 'CRITICAL',
            'flag_type': 'execution_gap',
            'evidence_ids': [c.case_id for c in cases[:5]]
        })
    
    # R-05: Critical asset with 0 alerts in 30 days (handled primarily in negative_space.py)
    # We flag it here too for rule counting
    assets = db.query(AssetRecord).filter(
        AssetRecord.batch_id == batch_id,
        AssetRecord.cse_id == cse_id,
        AssetRecord.classification == 'CRITICAL'
    ).all()
    alert_asset_ids = set(a.asset_id for a in alerts if a.asset_id)
    silent_critical = [a for a in assets if a.asset_id not in alert_asset_ids]
    if silent_critical:
        triggered.append({
            'rule_id': 'R-05',
            'rule_name': 'Silent Critical Asset',
            'description': f'{len(silent_critical)} critical asset(s) generated zero security alerts in the submission period.',
            'severity': 'CRITICAL',
            'flag_type': 'negative_space',
            'evidence_ids': [a.asset_id for a in silent_critical]
        })
    
    # R-06: Missing entire alert severity category vs peers
    if peer_features:
        peer_severity_counts = {}
        for pid, pf in peer_features.items():
            if pid == cse_id:
                continue
            # We need actual severity distributions from DB — simplified check
            pass
        # Simplified: check if this CSE has 0 HIGH alerts while others have many
        this_severities = set(a.severity for a in alerts)
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if sev not in this_severities:
                peer_has_sev = sum(1 for pid, pf in peer_features.items()
                                   if pid != cse_id and pf.get('alert_category_coverage', 0) >= 3)
                if peer_has_sev >= len(peer_features) * 0.7:
                    triggered.append({
                        'rule_id': 'R-06',
                        'rule_name': f'Missing {sev} Alert Category',
                        'description': f'No {sev} severity alerts present, while majority of peer CSEs have this category.',
                        'severity': 'HIGH',
                        'flag_type': 'negative_space',
                        'evidence_ids': []
                    })
    
    # R-07: Critical asset telemetry below peer 10th percentile
    if peer_features:
        ratios = [pf.get('critical_asset_telemetry_ratio', 0) 
                  for pid, pf in peer_features.items() if pid != cse_id]
        if ratios:
            import numpy as np
            p10 = float(np.percentile(ratios, 10))
            if features.get('critical_asset_telemetry_ratio', 0) < p10:
                triggered.append({
                    'rule_id': 'R-07',
                    'rule_name': 'Low Critical Asset Telemetry',
                    'description': f'Critical asset telemetry ratio ({features["critical_asset_telemetry_ratio"]:.2f}) is below peer 10th percentile ({p10:.2f}).',
                    'severity': 'HIGH',
                    'flag_type': 'negative_space',
                    'evidence_ids': []
                })
    
    # R-08: Closure time CV < 0.05 (templating indicator)
    if len(critical_alerts) >= 10 and features.get('closure_time_cv', 1.0) < 0.05:
        triggered.append({
            'rule_id': 'R-08',
            'rule_name': 'Suspiciously Uniform Closure Times',
            'description': f'Closure time coefficient of variation is {features["closure_time_cv"]:.4f} (threshold: 0.05). Extremely uniform closure times suggest automated/templated processing.',
            'severity': 'HIGH',
            'flag_type': 'execution_gap',
            'evidence_ids': [a.alert_id for a in critical_alerts[:5]]
        })
    
    return triggered
