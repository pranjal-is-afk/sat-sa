"""
Data Normalization & Sanitization Service
Transforms heterogeneous inputs into canonical records, normalizes timestamps,
and defangs dangerous spreadsheet formula injection characters.
"""

from typing import Dict, Any
from datetime import datetime

DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

def sanitize_text(val: Any) -> str:
    """Escapes CSV formula injection characters."""
    if val is None:
        return ""
    s = str(val)
    if s.startswith(DANGEROUS_PREFIXES):
        return "'" + s.strip()
    return s.strip()

def normalize_timestamp(ts_str: Any) -> str:
    """Converts diverse timestamp strings to standardized UTC ISO-8601."""
    if not ts_str:
        return None
    s = str(ts_str).strip()
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.rstrip("Z"))
        return dt.isoformat() + "Z"
    except Exception:
        return s

def normalize_alert_record(raw: Dict[str, Any], submission_id: str = None) -> Dict[str, Any]:
    return {
        "alert_id": sanitize_text(raw.get("alert_id")),
        "cse_id": sanitize_text(raw.get("cse_id")),
        "created_at": normalize_timestamp(raw.get("created_at")),
        "acknowledged_at": normalize_timestamp(raw.get("acknowledged_at")),
        "closed_at": normalize_timestamp(raw.get("closed_at")),
        "severity": sanitize_text(raw.get("severity", "Low")),
        "alert_category": sanitize_text(raw.get("alert_category", "Uncategorized")),
        "source_system": sanitize_text(raw.get("source_system", "")),
        "asset_id": sanitize_text(raw.get("asset_id", "")),
        "asset_criticality": sanitize_text(raw.get("asset_criticality", "Medium")),
        "status": sanitize_text(raw.get("status", "Open")),
        "disposition": sanitize_text(raw.get("disposition", "")),
        "case_id": sanitize_text(raw.get("case_id", "")) or None,
        "escalation_id": sanitize_text(raw.get("escalation_id", "")) or None,
        "analyst_id": sanitize_text(raw.get("analyst_id", "")),
        "business_service": sanitize_text(raw.get("business_service", "")),
        "submission_id": submission_id
    }

def normalize_case_record(raw: Dict[str, Any], submission_id: str = None) -> Dict[str, Any]:
    try:
        ev_count = int(raw.get("evidence_count", 0))
    except (ValueError, TypeError):
        ev_count = 0

    return {
        "case_id": sanitize_text(raw.get("case_id")),
        "cse_id": sanitize_text(raw.get("cse_id")),
        "alert_id": sanitize_text(raw.get("alert_id", "")) or None,
        "created_at": normalize_timestamp(raw.get("created_at")),
        "investigation_started_at": normalize_timestamp(raw.get("investigation_started_at")),
        "closed_at": normalize_timestamp(raw.get("closed_at")),
        "priority": sanitize_text(raw.get("priority", "Medium")),
        "investigation_summary": sanitize_text(raw.get("investigation_summary", "")),
        "evidence_count": ev_count,
        "closure_reason": sanitize_text(raw.get("closure_reason", "")),
        "root_cause": sanitize_text(raw.get("root_cause", "")),
        "remediation_status": sanitize_text(raw.get("remediation_status", "")),
        "reviewer_id": sanitize_text(raw.get("reviewer_id", "")),
        "submission_id": submission_id
    }
