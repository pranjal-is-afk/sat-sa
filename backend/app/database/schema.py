"""
Database Schema DDL & Initializer for SAT-SA
Creates canonical tables, submission tracker, data quality issues,
findings, dispositions, and cryptographic audit log.
"""

import sqlite3
from backend.app.database.connection import get_db_connection

DDL = """
-- 1. Critical Sector Entities
CREATE TABLE IF NOT EXISTS cse (
    cse_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT NOT NULL,
    criticality_tier TEXT NOT NULL,
    contact_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Periodic Submissions
CREATE TABLE IF NOT EXISTS submission (
    submission_id TEXT PRIMARY KEY,
    cse_id TEXT NOT NULL,
    reporting_period TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploader_id TEXT NOT NULL,
    file_count INTEGER DEFAULT 0,
    status TEXT NOT NULL, -- PENDING, VALIDATED, APPROVED, REJECTED
    FOREIGN KEY (cse_id) REFERENCES cse(cse_id)
);

-- 3. Raw Submission Files
CREATE TABLE IF NOT EXISTS submission_file (
    file_id TEXT PRIMARY KEY,
    submission_id TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    sha256_hash TEXT NOT NULL,
    row_count INTEGER DEFAULT 0,
    quarantined_count INTEGER DEFAULT 0,
    storage_path TEXT NOT NULL,
    FOREIGN KEY (submission_id) REFERENCES submission(submission_id)
);

-- 4. Data Quality Issues
CREATE TABLE IF NOT EXISTS data_quality_issue (
    issue_id TEXT PRIMARY KEY,
    submission_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    table_name TEXT NOT NULL,
    row_index INTEGER,
    record_id TEXT,
    field_name TEXT,
    invalid_value TEXT,
    error_message TEXT NOT NULL,
    status TEXT NOT NULL
);

-- 5. Asset Inventory
CREATE TABLE IF NOT EXISTS asset (
    asset_id TEXT NOT NULL,
    cse_id TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    business_service TEXT NOT NULL,
    criticality TEXT NOT NULL,
    environment TEXT,
    owner TEXT,
    monitoring_expected BOOLEAN NOT NULL DEFAULT 1,
    monitoring_source TEXT,
    PRIMARY KEY (cse_id, asset_id),
    FOREIGN KEY (cse_id) REFERENCES cse(cse_id)
);

-- 6. Canonical Alerts
CREATE TABLE IF NOT EXISTS alert (
    alert_id TEXT NOT NULL,
    cse_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    closed_at TIMESTAMP,
    severity TEXT NOT NULL,
    alert_category TEXT NOT NULL,
    source_system TEXT,
    asset_id TEXT,
    asset_criticality TEXT,
    status TEXT NOT NULL,
    disposition TEXT,
    case_id TEXT,
    escalation_id TEXT,
    analyst_id TEXT,
    business_service TEXT,
    submission_id TEXT,
    PRIMARY KEY (cse_id, alert_id),
    FOREIGN KEY (cse_id) REFERENCES cse(cse_id)
);

-- 7. Incident Cases
CREATE TABLE IF NOT EXISTS incident_case (
    case_id TEXT NOT NULL,
    cse_id TEXT NOT NULL,
    alert_id TEXT,
    created_at TIMESTAMP NOT NULL,
    investigation_started_at TIMESTAMP,
    closed_at TIMESTAMP,
    priority TEXT,
    investigation_summary TEXT,
    evidence_count INTEGER DEFAULT 0,
    closure_reason TEXT,
    root_cause TEXT,
    remediation_status TEXT,
    reviewer_id TEXT,
    submission_id TEXT,
    PRIMARY KEY (cse_id, case_id),
    FOREIGN KEY (cse_id) REFERENCES cse(cse_id)
);

-- 8. Investigation Steps
CREATE TABLE IF NOT EXISTS investigation_step (
    step_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    step_status TEXT NOT NULL,
    performed_by TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT,
    evidence_reference TEXT
);

-- 9. Escalations
CREATE TABLE IF NOT EXISTS escalation (
    escalation_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    escalation_level TEXT NOT NULL,
    escalated_to TEXT NOT NULL,
    escalated_at TIMESTAMP NOT NULL,
    reason TEXT NOT NULL,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    status TEXT NOT NULL
);

-- 10. Remediations
CREATE TABLE IF NOT EXISTS remediation (
    remediation_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    case_id TEXT,
    vulnerability_or_root_cause TEXT NOT NULL,
    action_plan TEXT NOT NULL,
    status TEXT NOT NULL,
    due_date DATE
);

-- 11. Telemetry Coverage
CREATE TABLE IF NOT EXISTS telemetry_coverage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cse_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    period TEXT NOT NULL,
    expected_event_volume INTEGER NOT NULL,
    observed_event_volume INTEGER NOT NULL,
    last_seen_at TIMESTAMP,
    coverage_status TEXT NOT NULL
);

-- 12. Supervisory Findings
CREATE TABLE IF NOT EXISTS finding (
    finding_id TEXT PRIMARY KEY,
    cse_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    category TEXT NOT NULL,
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    confidence REAL NOT NULL,
    status TEXT NOT NULL, -- OPEN, CONFIRMED, FALSE_POSITIVE, NEEDS_MORE_EVIDENCE, REMEDIATION_REQUIRED
    case_id TEXT,
    alert_id TEXT,
    asset_id TEXT,
    reason TEXT NOT NULL,
    evidence_json TEXT NOT NULL,
    peer_baseline TEXT,
    recommended_action TEXT NOT NULL,
    priority_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Finding Dispositions
CREATE TABLE IF NOT EXISTS finding_disposition (
    disposition_id TEXT PRIMARY KEY,
    finding_id TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    comment TEXT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (finding_id) REFERENCES finding(finding_id)
);

-- 14. Append-Only Cryptographic Audit Trail
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL,
    user_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    hash TEXT NOT NULL
);

-- 15. Entity Supervisory Risk Scores
CREATE TABLE IF NOT EXISTS entity_supervisory_risk (
    cse_id TEXT PRIMARY KEY,
    score REAL NOT NULL,
    risk_tier TEXT NOT NULL,
    sub_scores_json TEXT NOT NULL,
    contributors_json TEXT NOT NULL,
    findings_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cse_id) REFERENCES cse(cse_id)
);

-- Indexes for fast query performance
CREATE INDEX IF NOT EXISTS idx_alert_cse ON alert(cse_id);
CREATE INDEX IF NOT EXISTS idx_alert_sev ON alert(severity);
CREATE INDEX IF NOT EXISTS idx_case_cse ON incident_case(cse_id);
CREATE INDEX IF NOT EXISTS idx_finding_cse ON finding(cse_id);
CREATE INDEX IF NOT EXISTS idx_finding_sev ON finding(severity);
CREATE INDEX IF NOT EXISTS idx_finding_cat ON finding(category);
CREATE INDEX IF NOT EXISTS idx_finding_priority ON finding(priority_score DESC);
"""

def init_db():
    conn = get_db_connection()
    try:
        conn.executescript(DDL)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database schema initialized successfully.")
