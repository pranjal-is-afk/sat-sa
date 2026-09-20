"""
Submission Ingestion Service
Manages file ingestion, computes SHA-256 provenance hashes,
coordinates validation, and writes normalized canonical records into SQLite.
"""

import os
import csv
import json
import hashlib
from typing import List, Dict, Any, Tuple
import sqlite3
from pathlib import Path

from backend.app.config import RAW_DIR
from backend.app.services.validation_service import validate_submission_batch
from backend.app.services.normalization_service import normalize_alert_record, normalize_case_record
from backend.app.services.audit_service import log_audit_event

def compute_sha256(file_bytes: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()

def parse_csv_or_json(file_name: str, file_bytes: bytes) -> List[Dict[str, Any]]:
    text = file_bytes.decode("utf-8", errors="replace")
    if file_name.endswith(".json"):
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    else: # Default CSV
        reader = csv.DictReader(text.splitlines())
        return list(reader)

def process_submission_files(
    conn: sqlite3.Connection,
    cse_id: str,
    reporting_period: str,
    uploader_id: str,
    files_payload: List[Tuple[str, bytes]] # [(file_name, bytes), ...]
) -> Dict[str, Any]:
    submission_id = f"SUB-{cse_id}-{reporting_period}-{int(hashlib.md5(str(os.urandom(8)).encode()).hexdigest()[:6], 16)}"
    
    sub_raw_dir = RAW_DIR / submission_id
    sub_raw_dir.mkdir(parents=True, exist_ok=True)

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO submission (submission_id, cse_id, reporting_period, uploader_id, file_count, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (submission_id, cse_id, reporting_period, uploader_id, len(files_payload), "VALIDATED")
    )

    all_raw_alerts = []
    all_raw_cases = []
    all_raw_assets = []
    all_raw_steps = []
    all_raw_escalations = []
    all_raw_remediations = []
    all_raw_coverage = []

    for file_name, file_bytes in files_payload:
        f_hash = compute_sha256(file_bytes)
        f_path = sub_raw_dir / file_name
        with open(f_path, "wb") as f:
            f.write(file_bytes)

        parsed_rows = parse_csv_or_json(file_name, file_bytes)
        row_count = len(parsed_rows)
        lower_name = file_name.lower()

        f_type = "UNKNOWN"
        if "alert" in lower_name:
            f_type = "ALERTS"
            all_raw_alerts.extend(parsed_rows)
        elif "case" in lower_name:
            f_type = "CASES"
            all_raw_cases.extend(parsed_rows)
        elif "asset" in lower_name:
            f_type = "ASSETS"
            all_raw_assets.extend(parsed_rows)
        elif "step" in lower_name:
            f_type = "STEPS"
            all_raw_steps.extend(parsed_rows)
        elif "escalat" in lower_name:
            f_type = "ESCALATIONS"
            all_raw_escalations.extend(parsed_rows)
        elif "remediat" in lower_name:
            f_type = "REMEDIATIONS"
            all_raw_remediations.extend(parsed_rows)
        elif "coverage" in lower_name or "telemetry" in lower_name:
            f_type = "COVERAGE"
            all_raw_coverage.extend(parsed_rows)

        file_id = f"FIL-{submission_id[:12]}-{f_hash[:8]}"
        cursor.execute(
            "INSERT INTO submission_file (file_id, submission_id, file_type, file_name, file_size_bytes, sha256_hash, row_count, storage_path) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (file_id, submission_id, f_type, file_name, len(file_bytes), f_hash, row_count, str(f_path))
        )

    # Validate
    valid_alerts, valid_cases, issues = validate_submission_batch(
        submission_id, all_raw_alerts, all_raw_cases, all_raw_assets, all_raw_escalations
    )

    # Store Data Quality issues
    for iss in issues:
        cursor.execute(
            "INSERT INTO data_quality_issue (issue_id, submission_id, rule_id, severity, table_name, row_index, record_id, field_name, invalid_value, error_message, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (iss["issue_id"], submission_id, iss["rule_id"], iss["severity"], iss["table_name"], iss["row_index"], iss["record_id"], iss["field_name"], str(iss["invalid_value"]), iss["error_message"], iss["status"])
        )

    # Insert Normalized Valid Records
    for a in valid_alerts:
        na = normalize_alert_record(a, submission_id)
        cursor.execute(
            "INSERT OR REPLACE INTO alert (alert_id, cse_id, created_at, acknowledged_at, closed_at, severity, alert_category, source_system, asset_id, asset_criticality, status, disposition, case_id, escalation_id, analyst_id, business_service, submission_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (na["alert_id"], na["cse_id"], na["created_at"], na["acknowledged_at"], na["closed_at"], na["severity"], na["alert_category"], na["source_system"], na["asset_id"], na["asset_criticality"], na["status"], na["disposition"], na["case_id"], na["escalation_id"], na["analyst_id"], na["business_service"], submission_id)
        )

    for c in valid_cases:
        nc = normalize_case_record(c, submission_id)
        cursor.execute(
            "INSERT OR REPLACE INTO incident_case (case_id, cse_id, alert_id, created_at, investigation_started_at, closed_at, priority, investigation_summary, evidence_count, closure_reason, root_cause, remediation_status, reviewer_id, submission_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nc["case_id"], nc["cse_id"], nc["alert_id"], nc["created_at"], nc["investigation_started_at"], nc["closed_at"], nc["priority"], nc["investigation_summary"], nc["evidence_count"], nc["closure_reason"], nc["root_cause"], nc["remediation_status"], nc["reviewer_id"], submission_id)
        )

    for a in all_raw_assets:
        cursor.execute(
            "INSERT OR REPLACE INTO asset (asset_id, cse_id, asset_type, business_service, criticality, environment, owner, monitoring_expected, monitoring_source) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (a.get("asset_id"), a.get("cse_id"), a.get("asset_type", "Server"), a.get("business_service", "General"), a.get("criticality", "Medium"), a.get("environment", "Prod"), a.get("owner", ""), 1 if str(a.get("monitoring_expected", "true")).lower() in ["true", "1"] else 0, a.get("monitoring_source", ""))
        )

    for s in all_raw_steps:
        cursor.execute(
            "INSERT OR REPLACE INTO investigation_step (step_id, case_id, step_name, step_status, performed_by, started_at, completed_at, notes, evidence_reference) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (s.get("step_id"), s.get("case_id"), s.get("step_name", "Triage"), s.get("step_status", "Completed"), s.get("performed_by", ""), s.get("started_at"), s.get("completed_at"), s.get("notes", ""), s.get("evidence_reference", ""))
        )

    for e in all_raw_escalations:
        cursor.execute(
            "INSERT OR REPLACE INTO escalation (escalation_id, case_id, escalation_level, escalated_to, escalated_at, reason, acknowledged_at, resolved_at, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (e.get("escalation_id"), e.get("case_id"), e.get("escalation_level", "Tier-2"), e.get("escalated_to", "CERT"), e.get("escalated_at"), e.get("reason", ""), e.get("acknowledged_at"), e.get("resolved_at"), e.get("status", "Dispatched"))
        )

    for cov in all_raw_coverage:
        cursor.execute(
            "INSERT INTO telemetry_coverage (cse_id, asset_id, period, expected_event_volume, observed_event_volume, last_seen_at, coverage_status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (cov.get("cse_id", cse_id), cov.get("asset_id"), cov.get("period", reporting_period), int(cov.get("expected_event_volume") or 0), int(cov.get("observed_event_volume") or 0), cov.get("last_seen_at"), cov.get("coverage_status", "Active"))
        )

    for r in all_raw_remediations:
        cursor.execute(
            "INSERT OR REPLACE INTO remediation (remediation_id, asset_id, case_id, vulnerability_or_root_cause, action_plan, status, due_date) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (r.get("remediation_id"), r.get("asset_id"), r.get("case_id"), r.get("vulnerability_or_root_cause", ""), r.get("action_plan", ""), r.get("status", "Planned"), r.get("due_date"))
        )

    conn.commit()

    # Log cryptographic audit event
    log_audit_event(
        conn,
        action="SUBMISSION_INGESTED",
        user_id=uploader_id,
        payload={
            "submission_id": submission_id,
            "cse_id": cse_id,
            "period": reporting_period,
            "file_count": len(files_payload),
            "valid_alerts": len(valid_alerts),
            "valid_cases": len(valid_cases),
            "quarantined_issues": len(issues)
        }
    )

    return {
        "submission_id": submission_id,
        "cse_id": cse_id,
        "reporting_period": reporting_period,
        "files_processed": len(files_payload),
        "valid_alerts_count": len(valid_alerts),
        "valid_cases_count": len(valid_cases),
        "data_quality_issues_count": len(issues),
        "status": "VALIDATED"
    }
