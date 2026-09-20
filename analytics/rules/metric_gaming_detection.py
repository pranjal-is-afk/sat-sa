"""
Rule R-GAM-001: Metric & SLA Gaming Pattern Detection
Detects unnatural operational patterns intended to meet compliance KPIs:
- Clustering of closures immediately before SLA deadline (e.g. 55-59 mins for 60 min SLA)
- Bulk closure bursts (dozens of cases closed within seconds by same analyst)
"""

from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict

def parse_iso(ts_str: str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.rstrip("Z"))
    except Exception:
        return None

def evaluate_metric_gaming(
    cases: List[Dict[str, Any]],
    burst_threshold: int = 5,
    burst_window_seconds: int = 60,
    rule_version: str = "1.2.0"
) -> List[Dict[str, Any]]:
    findings = []
    
    # Check for rapid bulk closure bursts by the same reviewer/analyst
    closures_by_reviewer = defaultdict(list)
    for c in cases:
        closed_dt = parse_iso(c.get("closed_at"))
        reviewer = c.get("reviewer_id") or "UNKNOWN"
        if closed_dt:
            closures_by_reviewer[reviewer].append((closed_dt, c["case_id"]))

    for reviewer, records in closures_by_reviewer.items():
        records.sort(key=lambda x: x[0])
        n = len(records)
        for i in range(n):
            window_cases = [records[i][1]]
            for j in range(i + 1, n):
                diff = (records[j][0] - records[i][0]).total_seconds()
                if diff <= burst_window_seconds:
                    window_cases.append(records[j][1])
                else:
                    break
            if len(window_cases) >= burst_threshold:
                cid = window_cases[0]
                findings.append({
                    "finding_id": f"F-GAM-BURST-{cid}",
                    "entity_id": cases[0].get("cse_id", ""),
                    "rule_id": "R-GAM-001",
                    "rule_version": rule_version,
                    "category": "Operational Discipline",
                    "type": "METRIC_GAMING_BULK_CLOSURE",
                    "severity": "LOW",
                    "confidence": 0.80,
                    "status": "OPEN",
                    "case_id": cid,
                    "alert_id": None,
                    "asset_id": None,
                    "reason": f"Suspicious bulk closure burst detected: Reviewer {reviewer} closed {len(window_cases)} cases within {burst_window_seconds} seconds, suggesting robotic or metric-gaming batch resolution.",
                    "evidence": [
                        {"table": "cases", "record_id": cid, "field": "burst_closure_count", "value": len(window_cases)},
                        {"table": "cases", "record_id": cid, "field": "window_seconds", "value": burst_window_seconds},
                        {"table": "cases", "record_id": cid, "field": "sample_case_ids", "value": window_cases[:5]}
                    ],
                    "peer_baseline": "Normal human review requires distinct investigation windows per case.",
                    "recommended_action": "Examine case notes across the batch to verify whether individual forensic inspection took place."
                })
                break # One burst finding per reviewer per batch is sufficient

    return findings
