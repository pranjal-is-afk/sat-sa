import numpy as np
from typing import Dict, List, Tuple

def compute_composite_score(
    cse_id: str,
    rules_triggered: List[dict],
    z_scores: dict,
    peer_ranks: dict,
    neg_space_findings: List[dict],
    alert_count: int,
    all_rules_count: int = 8
) -> Tuple[dict, float]:
    """Compute weighted composite risk score 0-100."""
    
    # Component 1: Rule violations (30%)
    rule_weights = {'CRITICAL': 30.0, 'HIGH': 20.0, 'MEDIUM': 10.0, 'LOW': 5.0}
    rules_score_raw = sum(rule_weights.get(r.get('severity', 'HIGH'), 20.0) for r in rules_triggered)
    rules_score = min(rules_score_raw, 100.0)
    
    # Component 2: Statistical deviation via directional Z-scores (25%)
    risky_when_low = {'mean_closure_time_critical', 'escalation_rate', 'closure_time_cv', 'case_linkage_rate'}
    risky_when_high = {'critical_fast_closure_rate', 'investigation_text_similarity', 'low_activity_window_count'}
    
    risk_zs = []
    for feat in risky_when_low:
        z = z_scores.get(feat, 0.0)
        risk_zs.append(max(-z, 0.0))
        
    for feat in risky_when_high:
        z = z_scores.get(feat, 0.0)
        risk_zs.append(max(z, 0.0))
    
    mean_risk_z = float(np.mean(risk_zs)) if risk_zs else 0.0
    z_score_component = min((mean_risk_z / 1.5) * 100.0, 100.0)
    
    # Component 3: Peer benchmarking (25%)
    # For protective features: lower rank = higher risk (100 - rank)
    # For harmful features: higher rank = higher risk (rank)
    protective_ranks = ['escalation_rate', 'critical_asset_telemetry_ratio', 'alert_category_coverage', 'mean_closure_time_critical']
    harmful_ranks = ['critical_fast_closure_rate']
    
    peer_risks = []
    for f in protective_ranks:
        rank = peer_ranks.get(f, 50.0)
        peer_risks.append(100.0 - rank)
        
    for f in harmful_ranks:
        rank = peer_ranks.get(f, 50.0)
        peer_risks.append(rank)
        
    peer_component = float(np.mean(peer_risks)) if peer_risks else 50.0
    
    # Component 4: Negative space (20%)
    severity_weights = {'CRITICAL': 35.0, 'HIGH': 25.0, 'MEDIUM': 15.0, 'LOW': 5.0}
    neg_space_raw = sum(severity_weights.get(f.get('severity', 'LOW'), 5.0) 
                        for f in neg_space_findings)
    neg_space_component = min(neg_space_raw, 100.0)
    
    # Weighted composite
    composite = (
        0.30 * rules_score +
        0.25 * z_score_component +
        0.25 * peer_component +
        0.20 * neg_space_component
    )
    composite = float(np.clip(composite, 0.0, 100.0))
    
    score_breakdown = {
        'rules': round(rules_score, 1),
        'statistical': round(z_score_component, 1),
        'peer': round(peer_component, 1),
        'negative_space': round(neg_space_component, 1),
    }
    
    return score_breakdown, composite


def classify_risk(composite: float, alert_count: int, rules_triggered: List[dict],
                  neg_space_findings: List[dict]) -> Tuple[str, bool, str]:
    """Return (risk_level, is_grey, primary_reason)."""
    if alert_count < 50:
        return 'UNASSESSED', True, 'Insufficient data for assessment (<50 alerts)'
    
    if composite >= 75:
        level = 'CRITICAL'
    elif composite >= 50:
        level = 'HIGH'
    elif composite >= 25:
        level = 'MEDIUM'
    else:
        level = 'LOW'
    
    # Primary reason: first triggered rule or first neg space finding
    if rules_triggered:
        primary = rules_triggered[0]['rule_name']
    elif neg_space_findings:
        primary = f"Negative space: {neg_space_findings[0]['description'][:80]}"
    else:
        primary = 'Composite statistical deviation'
    
    return level, False, primary
