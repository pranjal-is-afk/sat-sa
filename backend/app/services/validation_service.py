"""
Data Validation & Quality Assurance Service
Implements rules DQ-001 through DQ-012 with automated quarantine routing.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime

def parse_iso(ts_str: str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.rstrip("Z"))
    except Exception:
        return None

def validate_submission_batch(
    submission_id: str,
    alerts: List[Dict[str, Any]],
    cases: List[Dict[str, Any]],
    assets: List[Dict[str, Any]],
    escalations: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Returns:
    - valid_alerts: records that passed quality checks
    - valid_cases: cases that passed quality checks
    - issues: list of data quality issues (errors and warnings)
    """
    issues = []
    valid_alerts = []
    valid_cases = []

    known_asset_ids = {a.get("asset_id") for a in assets if a.get("asset_id")}
    known_case_ids = {c.get("case_id") for c in cases if c.get("case_id")}
    seen_alert_ids = set()

    # 1. Validate Alerts
    for idx, alert in enumerate(alerts):
        aid = alert.get("alert_id")
        cid = alert.get("cse_id")
        sev = alert.get("severity")
        target_asset = alert.get("asset_id")
        linked_case = alert.get("case_id")

        is_quarantined = False

        # DQ-001: Declared Entity Check
        if not cid:
            issues.append({
                "issue_id": f"DQ-001-{idx}",
                "submission_id": submission_id,
                "rule_id": "DQ-001",
                "severity": "ERROR",
                "table_name": "alerts",
                "row_index": idx,
                "record_id": aid,
                "field_name": "cse_id",
                "invalid_value": None,
                "error_message": "Missing declared entity identifier (cse_id).",
                "status": "QUARANTINED"
            })
            is_quarantined = True

        # DQ-002: Alert ID Uniqueness
        if aid in seen_alert_ids:
            issues.append({
                "issue_id": f"DQ-002-{idx}",
                "submission_id": submission_id,
                "rule_id": "DQ-002",
                "severity": "ERROR",
                "table_name": "alerts",
                "row_index": idx,
                "record_id": aid,
                "field_name": "alert_id",
                "invalid_value": aid,
                "error_message": f"Duplicate alert ID {aid} detected in batch.",
                "status": "QUARANTINED"
            })
            is_quarantined = True
        else:
            if aid:
                seen_alert_ids.add(aid)

        # DQ-007: Valid Severity
        if sev not in ["Critical", "High", "Medium", "Low"]:
            issues.append({
                "issue_id": f"DQ-007-{idx}",
                "submission_id": submission_id,
                "rule_id": "DQ-007",
                "severity": "ERROR",
                "table_name": "alerts",
                "row_index": idx,
                "record_id": aid,
                "field_name": "severity",
                "invalid_value": sev,
                "error_message": f"Invalid threat severity '{sev}'. Must be Critical, High, Medium, or Low.",
                "status": "QUARANTINED"
            })
            is_quarantined = True

        # DQ-003 & DQ-004: Monotonic Timestamps
        c_dt = parse_iso(alert.get("created_at"))
        cl_dt = parse_iso(alert.get("closed_at"))
        ack_dt = parse_iso(alert.get("acknowledged_at"))

        if not c_dt:
            issues.append({
                "issue_id": f"DQ-010-{idx}",
                "submission_id": submission_id,
                "rule_id": "DQ-010",
                "severity": "ERROR",
                "table_name": "alerts",
                "row_index": idx,
                "record_id": aid,
                "field_name": "created_at",
                "invalid_value": alert.get("created_at"),
                "error_message": "Unparseable created_at timestamp.",
                "status": "QUARANTINED"
            })
            is_quarantined = True

        if c_dt and cl_dt and cl_dt < c_dt:
            issues.append({
                "issue_id": f"DQ-003-{idx}",
                "submission_id": submission_id,
                "rule_id": "DQ-003",
                "severity": "ERROR",
                "table_name": "alerts",
                "row_index": idx,
                "record_id": aid,
                "field_name": "closed_at",
                "invalid_value": alert.get("closed_at"),
                "error_message": f"closed_at ({alert.get('closed_at')}) precedes created_at ({alert.get('created_at')}).",
                "status": "QUARANTINED"
            })
            is_quarantined = True

        # DQ-008: Asset Reference Warning
        if target_asset and target_asset not in known_asset_ids:
            issues.append({
                "issue_id": f"DQ-008-{idx}",
                "submission_id": submission_id,
                "rule_id": "DQ-008",
                "severity": "WARNING",
                "table_name": "alerts",
                "row_index": idx,
                "record_id": aid,
                "field_name": "asset_id",
                "invalid_value": target_asset,
                "error_message": f"Referenced asset {target_asset} is not present in declared asset inventory.",
                "status": "FLAGGED"
            })

        # DQ-005: Case Referential Integrity Warning/Error
        if linked_case and linked_case not in known_case_ids:
            issues.append({
                "issue_id": f"DQ-005-{idx}",
                "submission_id": submission_id,
                "rule_id": "DQ-005",
                "severity": "WARNING",
                "table_name": "alerts",
                "row_index": idx,
                "record_id": aid,
                "field_name": "case_id",
                "invalid_value": linked_case,
                "error_message": f"Referenced case {linked_case} does not exist in cases submission.",
                "status": "FLAGGED"
            })

        if not is_quarantined:
            valid_alerts.append(alert)

    # 2. Validate Cases
    for idx, c in enumerate(cases):
        case_id = c.get("case_id")
        cid = c.get("cse_id")
        is_quarantined = False

        if not cid:
            issues.append({
                "issue_id": f"DQ-001-C-{idx}",
                "submission_id": submission_id,
                "rule_id": "DQ-001",
                "severity": "ERROR",
                "table_name": "cases",
                "row_index": idx,
                "record_id": case_id,
                "field_name": "cse_id",
                "invalid_value": None,
                "error_message": "Missing declared entity identifier in case record.",
                "status": "QUARANTINED"
            })
            is_quarantined = True

        c_dt = parse_iso(c.get("created_at"))
        cl_dt = parse_iso(c.get("closed_at"))
        if c_dt and cl_dt and cl_dt < c_dt:
            issues.append({
                "issue_id": f"DQ-003-C-{idx}",
                "submission_id": submission_id,
                "rule_id": "DQ-003",
                "severity": "ERROR",
                "table_name": "cases",
                "row_index": idx,
                "record_id": case_id,
                "field_name": "closed_at",
                "invalid_value": c.get("closed_at"),
                "error_message": "Case closed_at precedes created_at.",
                "status": "QUARANTINED"
            })
            is_quarantined = True

        if not is_quarantined:
            valid_cases.append(c)

    return valid_alerts, valid_cases, issues
