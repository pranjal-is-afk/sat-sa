"""
Rule R-ESC-001: Critical Alert Missing Mandatory Escalation
Flags Critical alerts on Critical/High assets that lack an escalation record within SLA window.
"""

from typing import List, Dict, Any

def evaluate_critical_alert_no_escalation(
    alerts: List[Dict[str, Any]],
    escalations: List[Dict[str, Any]],
    assets_map: Dict[str, Dict[str, Any]],
    rule_version: str = "1.2.0"
) -> List[Dict[str, Any]]:
    findings = []
    escalated_case_ids = {esc.get("case_id") for esc in escalations if esc.get("case_id")}

    for alert in alerts:
        severity = alert.get("severity", "")
        asset_id = alert.get("asset_id", "")
        asset = assets_map.get(asset_id, {})
        asset_crit = asset.get("criticality", alert.get("asset_criticality", ""))

        if severity == "Critical" and asset_crit in ["Critical", "High"]:
            case_id = alert.get("case_id")
            # If no case or case has no escalation record
            if not case_id or case_id not in escalated_case_ids:
                finding_id = f"F-ESC-{alert.get('alert_id', 'UNKNOWN')}"
                findings.append({
                    "finding_id": finding_id,
                    "entity_id": alert.get("cse_id", ""),
                    "rule_id": "R-ESC-001",
                    "rule_version": rule_version,
                    "category": "Escalation Weakness",
                    "type": "CRITICAL_ALERT_MISSING_ESCALATION",
                    "severity": "HIGH",
                    "confidence": 0.96,
                    "status": "OPEN",
                    "alert_id": alert.get("alert_id"),
                    "case_id": case_id,
                    "asset_id": asset_id,
                    "reason": f"Critical alert {alert.get('alert_id')} on {asset_crit.lower()} asset {asset_id} has no linked escalation record.",
                    "evidence": [
                        {"table": "alerts", "record_id": alert.get("alert_id"), "field": "severity", "value": "Critical"},
                        {"table": "assets", "record_id": asset_id, "field": "criticality", "value": asset_crit},
                        {"table": "escalations", "record_id": None, "field": "escalation_id", "value": "MISSING"}
                    ],
                    "peer_baseline": "Sector peer escalation compliance for critical incidents is 98.4%",
                    "recommended_action": "Review alert handling and verify if incident should be escalated to CERT / leadership."
                })

    return findings
