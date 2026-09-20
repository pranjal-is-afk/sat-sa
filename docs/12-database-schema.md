# 12. Database Schema Document

## 1. Schema Overview & Design Principles
- **Engine**: SQLite 3 with Write-Ahead Logging (WAL) enabled (`PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;`).
- **Audit Immutability**: The `audit_events` table is append-only. Deletions and updates are strictly prevented.
- **Relational Integrity**: Foreign keys link alerts to cases, cases to investigation steps, and findings to source evidence records.

## 2. Entity-Relationship Diagram (ERD)
```
┌──────────────┐          1..N       ┌────────────────┐
│     CSE      ├────────────────────►│   SUBMISSION   │
└──────┬───────┘                     └───────┬────────┘
       │                                     │
       │ 1..N                                │ 1..N
       ▼                                     ▼
┌──────────────┐          1..N       ┌────────────────┐
│    ASSET     │◄────────────────────┤     ALERT      │
└──────┬───────┘                     └───────┬────────┘
       │                                     │ 0..1
       │ 1..N                                ▼
       │                             ┌────────────────┐
       └────────────────────────────►│      CASE      │
                                     └───────┬────────┘
                                             │
                       ┌─────────────────────┼─────────────────────┐
                       │ 1..N                │ 0..N                │ 0..N
                       ▼                     ▼                     ▼
              ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
              │INVESTIGATION_STEP│  │   ESCALATION    │   │   REMEDIATION   │
              └─────────────────┘   └─────────────────┘   └─────────────────┘
```

## 3. Database Table Definitions (DDL)

```sql
-- 1. Critical Sector Entities
CREATE TABLE cse (
    cse_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT NOT NULL,
    criticality_tier TEXT NOT NULL,
    contact_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Submissions
CREATE TABLE submission (
    submission_id TEXT PRIMARY KEY,
    cse_id TEXT NOT NULL,
    reporting_period TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploader_id TEXT NOT NULL,
    file_count INTEGER DEFAULT 0,
    status TEXT NOT NULL, -- PENDING, VALIDATED, APPROVED, REJECTED
    FOREIGN KEY (cse_id) REFERENCES cse(cse_id)
);

-- 3. Raw Submission Files & Lineage Hashes
CREATE TABLE submission_file (
    file_id TEXT PRIMARY KEY,
    submission_id TEXT NOT NULL,
    file_type TEXT NOT NULL, -- ALERTS, CASES, ASSETS, STEPS, ESCALATIONS, COVERAGE, REMEDIATIONS
    file_name TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    sha256_hash TEXT NOT NULL,
    row_count INTEGER DEFAULT 0,
    quarantined_count INTEGER DEFAULT 0,
    storage_path TEXT NOT NULL,
    FOREIGN KEY (submission_id) REFERENCES submission(submission_id)
);

-- 4. Data Quality Issues Log
CREATE TABLE data_quality_issue (
    issue_id TEXT PRIMARY KEY,
    submission_id TEXT NOT NULL,
    rule_id TEXT NOT NULL, -- DQ-001 to DQ-012
    severity TEXT NOT NULL, -- ERROR, WARNING
    table_name TEXT NOT NULL,
    row_index INTEGER,
    record_id TEXT,
    field_name TEXT,
    invalid_value TEXT,
    error_message TEXT NOT NULL,
    status TEXT NOT NULL -- QUARANTINED, MERGED, IGNORED
);

-- 5. Asset Inventory
CREATE TABLE asset (
    asset_id TEXT NOT NULL,
    cse_id TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    business_service TEXT NOT NULL,
    criticality TEXT NOT NULL, -- Critical, High, Medium, Low
    environment TEXT,
    monitoring_expected BOOLEAN NOT NULL DEFAULT 1,
    monitoring_source TEXT,
    PRIMARY KEY (cse_id, asset_id),
    FOREIGN KEY (cse_id) REFERENCES cse(cse_id)
);

-- 6. Canonical Alerts
CREATE TABLE alert (
    alert_id TEXT NOT NULL,
    cse_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    closed_at TIMESTAMP,
    severity TEXT NOT NULL, -- Critical, High, Medium, Low
    alert_category TEXT NOT NULL,
    source_system TEXT,
    asset_id TEXT,
    status TEXT NOT NULL,
    disposition TEXT,
    case_id TEXT,
    escalation_id TEXT,
    analyst_id TEXT,
    business_service TEXT,
    submission_id TEXT NOT NULL,
    PRIMARY KEY (cse_id, alert_id),
    FOREIGN KEY (cse_id) REFERENCES cse(cse_id)
);

-- 7. Canonical Cases
CREATE TABLE incident_case (
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
    submission_id TEXT NOT NULL,
    PRIMARY KEY (cse_id, case_id),
    FOREIGN KEY (cse_id) REFERENCES cse(cse_id)
);

-- 8. Investigation Steps
CREATE TABLE investigation_step (
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

-- 9. Escalation Records
CREATE TABLE escalation (
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

-- 10. Remediation Records
CREATE TABLE remediation (
    remediation_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    case_id TEXT,
    vulnerability_or_root_cause TEXT NOT NULL,
    action_plan TEXT NOT NULL,
    status TEXT NOT NULL,
    due_date DATE
);

-- 11. Telemetry Coverage (Negative Space Base)
CREATE TABLE telemetry_coverage (
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
CREATE TABLE finding (
    finding_id TEXT PRIMARY KEY,
    cse_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    category TEXT NOT NULL,
    type TEXT NOT NULL,
    severity TEXT NOT NULL, -- CRITICAL, HIGH, MEDIUM, LOW
    confidence REAL NOT NULL,
    status TEXT NOT NULL, -- OPEN, CONFIRMED, REJECTED, REMEDIATION_REQUIRED
    case_id TEXT,
    alert_id TEXT,
    asset_id TEXT,
    reason TEXT NOT NULL,
    evidence_json TEXT NOT NULL,
    peer_baseline TEXT,
    recommended_action TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Human Review Dispositions
CREATE TABLE finding_disposition (
    disposition_id TEXT PRIMARY KEY,
    finding_id TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    decision TEXT NOT NULL, -- Confirmed, Not Substantiated, False Positive, etc.
    comment TEXT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (finding_id) REFERENCES finding(finding_id)
);

-- 14. Append-Only Cryptographic Audit Trail
CREATE TABLE audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL,
    user_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    hash TEXT NOT NULL
);
```
