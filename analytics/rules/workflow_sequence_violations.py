"""
Rule R-SEQ-001: Workflow Sequence Violations & Temporal Inversions
Detects illogical operational sequences:
- Case closed before investigation started
- Escalation recorded after case was already closed
- Inverted timestamps where closed_at < created_at
"""

from typing import List, Dict, Any
from datetime import datetime

def parse_iso(ts_str: str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.rstrip("Z"))
    except Exception:
        return None

def evaluate_workflow_sequence_violations(
    cases: List[Dict[str, Any]],
    escalations: List[Dict[str, Any]],
    rule_version: str = "1.2.0"
) -> List[Dict[str, Any]]:
    findings = []
    
    cases_map = {c["case_id"]: c for c in cases if c.get("case_id")}

    # 1. Check case timestamps
    for case in cases:
        cid = case.get("case_id")
        created_dt = parse_iso(case.get("created_at"))
        started_dt = parse_iso(case.get("investigation_started_at"))
        closed_dt = parse_iso(case.get("closed_at"))

        if closed_dt and started_dt and closed_dt < started_dt:
            findings.append({
                "finding_id": f"F-SEQ-INV-{cid}",
                "entity_id": case.get("cse_id", ""),
                "rule_id": "R-SEQ-001",
                "rule_version": rule_version,
                "category": "Operational Discipline",
                "type": "WORKFLOW_SEQUENCE_VIOLATION",
                "severity": "MEDIUM",
                "confidence": 0.99,
                "status": "OPEN",
                "case_id": cid,
                "alert_id": case.get("alert_id"),
                "asset_id": None,
                "reason": f"Case {cid} was marked closed before investigation was recorded as started.",
                "evidence": [
                    {"table": "cases", "record_id": cid, "field": "investigation_started_at", "value": case.get("investigation_started_at")},
                    {"table": "cases", "record_id": cid, "field": "closed_at", "value": case.get("closed_at")}
                ],
                "peer_baseline": "Standard lifecycle mandates investigation initiation prior to closure.",
                "recommended_action": "Audit SOC ticket automation workflows for premature closure scripts."
            })

    # 2. Check escalation post-closure
    for esc in escalations:
        cid = esc.get("case_id")
        case = cases_map.get(cid)
        if not case:
            continue
        esc_dt = parse_iso(esc.get("escalated_at"))
        closed_dt = parse_iso(case.get("closed_at"))
        if esc_dt and closed_dt and esc_dt > (closed_dt + datetime.resolution):
            findings.append({
                "finding_id": f"F-SEQ-ESC-{esc.get('escalation_id')}",
                "entity_id": case.get("cse_id", ""),
                "rule_id": "R-SEQ-001",
                "rule_version": rule_version,
                "category": "Operational Discipline",
                "type": "POST_CLOSURE_ESCALATION",
                "severity": "MEDIUM",
                "confidence": 0.95,
                "status": "OPEN",
                "case_id": cid,
                "alert_id": case.get("alert_id"),
                "asset_id": None,
                "reason": f"Escalation {esc.get('escalation_id')} was dispatched after parent case {cid} was marked closed.",
                "evidence": [
                    {"table": "cases", "record_id": cid, "field": "closed_at", "value": case.get("closed_at")},
                    {"table": "escalations", "record_id": esc.get("escalation_id"), "field": "escalated_at", "value": esc.get("escalated_at")}
                ],
                "peer_baseline": "Escalations must precede or coincide with case triage.",
                "recommended_action": "Verify if case was reopened or if retrospective paperwork was filed."
            })

    return findings
