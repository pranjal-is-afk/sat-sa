"""
Rule R-BEN-001: Statistical Peer Deviation & Low Activity Anomaly
Uses robust non-parametric statistics (Median, Interquartile Range, Percentiles)
to benchmark entities against sector cohorts while controlling for asset count and days.
"""

from typing import List, Dict, Any
import numpy as np

def compute_peer_metrics(
    entity_summaries: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes sector peer distributions for:
    - Alert rate per asset-day
    - Median closure minutes
    - Escalation percentage
    """
    if not entity_summaries:
        return {}

    rates = [e["alert_rate"] for e in entity_summaries]
    closures = [e["median_closure_mins"] for e in entity_summaries if e.get("median_closure_mins")]
    esc_rates = [e["escalation_rate"] for e in entity_summaries]

    metrics = {
        "alert_rate_median": float(np.median(rates)) if rates else 0.0,
        "alert_rate_p05": float(np.percentile(rates, 5)) if rates else 0.0,
        "alert_rate_p95": float(np.percentile(rates, 95)) if rates else 0.0,
        "closure_median": float(np.median(closures)) if closures else 54.0,
        "closure_p05": float(np.percentile(closures, 5)) if closures else 12.0,
        "escalation_rate_median": float(np.median(esc_rates)) if esc_rates else 0.85
    }
    return metrics

def evaluate_peer_deviations(
    cse_id: str,
    entity_stats: Dict[str, Any],
    peer_metrics: Dict[str, Any],
    rule_version: str = "1.2.0"
) -> List[Dict[str, Any]]:
    findings = []
    
    alert_rate = entity_stats.get("alert_rate", 0.0)
    p05 = peer_metrics.get("alert_rate_p05", 0.0)
    median = peer_metrics.get("alert_rate_median", 0.0)

    # Flag suspiciously low alert volume (e.g. broken sensor feed)
    if alert_rate < p05 and median > 0:
        findings.append({
            "finding_id": f"F-BEN-LOW-{cse_id}",
            "entity_id": cse_id,
            "rule_id": "R-BEN-001",
            "rule_version": rule_version,
            "category": "Peer Deviation",
            "type": "SUSPICIOUSLY_LOW_ACTIVITY_RATE",
            "severity": "MEDIUM",
            "confidence": 0.85,
            "status": "OPEN",
            "case_id": None,
            "alert_id": None,
            "asset_id": None,
            "reason": f"Entity normalized alert rate ({alert_rate:.3f} alerts/asset-day) is far below peer 5th percentile ({p05:.3f}) and peer median ({median:.3f}), indicating possible ingestion outages or unmonitored infrastructure.",
            "evidence": [
                {"table": "entities", "record_id": cse_id, "field": "alert_rate_per_asset_day", "value": round(alert_rate, 3)},
                {"table": "peers", "record_id": "SECTOR_BASELINE", "field": "peer_p05", "value": round(p05, 3)},
                {"table": "peers", "record_id": "SECTOR_BASELINE", "field": "peer_median", "value": round(median, 3)}
            ],
            "peer_baseline": f"Sector median alert generation rate is {median:.3f} alerts per asset-day.",
            "recommended_action": "Verify if syslog / telemetry collectors were offline or throttled during the reporting period."
        })

    return findings
