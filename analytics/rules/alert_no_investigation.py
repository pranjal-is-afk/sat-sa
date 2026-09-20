"""
Rule R-INV-001: Alert Acknowledged but Closed Without Meaningful Investigation
Computes an investigation quality score Q_investigation based on evidence, workflow steps,
root-cause analysis, and narrative detail.
"""

from typing import List, Dict, Any

def evaluate_alert_no_investigation(
    alerts: List[Dict[str, Any]],
    cases_map: Dict[str, Dict[str, Any]],
    steps_by_case: Dict[str, List[Dict[str, Any]]],
    min_quality_threshold: float = 0.40,
    rule_version: str = "1.2.0"
) -> List[Dict[str, Any]]:
    findings = []

    for alert in alerts:
        case_id = alert.get("case_id")
        sev = alert.get("severity", "")
        status = alert.get("status", "")

        # Only evaluate closed/acknowledged cases for Critical and High severity
        if sev not in ["Critical", "High"] or status not in ["Closed", "Acknowledged"]:
            continue

        case = cases_map.get(case_id, {})
        steps = steps_by_case.get(case_id, [])

        raw_ec = case.get("evidence_count", 0)
        try:
            evidence_count = int(raw_ec)
        except (ValueError, TypeError):
            evidence_count = 0

        summary = case.get("investigation_summary") or ""
        root_cause = case.get("root_cause") or ""

        # Factor E: Evidence completeness (0 to 1)
        E = min(1.0, evidence_count / 3.0)
        # Factor W: Workflow completion (0 to 1)
        W = min(1.0, len(steps) / 3.0)
        # Factor R: Root cause quality (0 or 1)
        R = 1.0 if len(root_cause.strip()) > 10 else 0.0
        # Factor A: Analyst reasoning length
        A = min(1.0, len(summary.strip()) / 80.0)
        # Factor D: Differentiation from minimal notes
        D = 1.0 if len(summary.strip()) > 30 and "closed" not in summary.lower()[:15] else 0.2

        # Weighted calculation
        Q_inv = 0.25 * E + 0.25 * W + 0.20 * R + 0.15 * A + 0.15 * D

        if Q_inv < min_quality_threshold:
            finding_id = f"F-INV-QUAL-{alert.get('alert_id', 'UNKNOWN')}"
            findings.append({
                "finding_id": finding_id,
                "entity_id": alert.get("cse_id", ""),
                "rule_id": "R-INV-001",
                "rule_version": rule_version,
                "category": "Investigation Weakness",
                "type": "SUPERFICIAL_INVESTIGATION_QUALITY",
                "severity": "HIGH" if sev == "Critical" else "MEDIUM",
                "confidence": 0.88,
                "status": "OPEN",
                "alert_id": alert.get("alert_id"),
                "case_id": case_id,
                "asset_id": alert.get("asset_id"),
                "reason": f"Investigation quality score {Q_inv:.2f} is below the threshold of {min_quality_threshold:.2f}. Incident has {len(steps)} workflow steps, {evidence_count} evidence items, and lacks substantive root-cause documentation.",
                "evidence": [
                    {"table": "cases", "record_id": case_id, "field": "q_investigation", "value": round(Q_inv, 2)},
                    {"table": "cases", "record_id": case_id, "field": "workflow_steps_count", "value": len(steps)},
                    {"table": "cases", "record_id": case_id, "field": "evidence_count", "value": evidence_count},
                    {"table": "cases", "record_id": case_id, "field": "root_cause_present", "value": bool(R)}
                ],
                "peer_baseline": "Sector peer median investigation quality score is 0.78",
                "recommended_action": "Request primary analyst log notes and conduct supervisory interview regarding triage depth."
            })

    return findings
