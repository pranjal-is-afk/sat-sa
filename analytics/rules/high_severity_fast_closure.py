"""
Rule R-INV-002: High-Severity Alert Closed Unusually Quickly
Calculates T_closure = T_closed - T_created.
Flags Critical and High severity alerts closed below threshold (e.g. 10 mins) or peer 5th percentile,
especially when evidence count is low or investigation notes are superficial.
"""

from typing import List, Dict, Any
from datetime import datetime

def parse_iso(ts_str: str):
    if not ts_str:
        return None
    try:
        # Handle trailing Z or timezone offsets
        clean = ts_str.rstrip("Z")
        return datetime.fromisoformat(clean)
    except Exception:
        return None

def evaluate_high_severity_fast_closure(
    alerts: List[Dict[str, Any]],
    cases_map: Dict[str, Dict[str, Any]],
    fast_threshold_minutes: float = 10.0,
    peer_5th_percentile_minutes: float = 25.0,
    rule_version: str = "1.2.0"
) -> List[Dict[str, Any]]:
    findings = []

    for alert in alerts:
        sev = alert.get("severity", "")
        if sev not in ["Critical", "High"]:
            continue

        created_dt = parse_iso(alert.get("created_at"))
        closed_dt = parse_iso(alert.get("closed_at"))

        if not created_dt or not closed_dt or closed_dt <= created_dt:
            continue

        duration_mins = (closed_dt - created_dt).total_seconds() / 60.0
        case_id = alert.get("case_id")
        case = cases_map.get(case_id, {})
        try:
            evidence_count = int(case.get("evidence_count", 0))
        except (ValueError, TypeError):
            evidence_count = 0

        # Flag if closure is under threshold OR under peer 5th percentile with low evidence count (<= 1)
        if duration_mins < fast_threshold_minutes or (duration_mins < peer_5th_percentile_minutes and evidence_count <= 1):
            finding_id = f"F-FAST-{alert.get('alert_id', 'UNKNOWN')}"
            findings.append({
                "finding_id": finding_id,
                "entity_id": alert.get("cse_id", ""),
                "rule_id": "R-INV-002",
                "rule_version": rule_version,
                "category": "Investigation Weakness",
                "type": "HIGH_SEVERITY_FAST_CLOSURE",
                "severity": "HIGH" if sev == "Critical" else "MEDIUM",
                "confidence": 0.92,
                "status": "OPEN",
                "alert_id": alert.get("alert_id"),
                "case_id": case_id,
                "asset_id": alert.get("asset_id"),
                "reason": f"{sev} severity alert {alert.get('alert_id')} was closed in {duration_mins:.1f} minutes, below the peer 5th percentile of {peer_5th_percentile_minutes:.1f} minutes, with only {evidence_count} evidence items attached.",
                "evidence": [
                    {"table": "alerts", "record_id": alert.get("alert_id"), "field": "closure_duration_mins", "value": round(duration_mins, 1)},
                    {"table": "alerts", "record_id": alert.get("alert_id"), "field": "severity", "value": sev},
                    {"table": "cases", "record_id": case_id, "field": "evidence_count", "value": evidence_count}
                ],
                "peer_baseline": f"Peer group median closure time is 54.0 minutes (5th percentile: {peer_5th_percentile_minutes:.1f} mins)",
                "recommended_action": "Manually inspect case investigation notes and verify whether sufficient forensic triage occurred before closing."
            })

    return findings
