# 17. Operational Runbook (ODD)

## 1. Scope & Administrative Procedures
This operational runbook provides standard operating procedures (SOPs) for maintaining, troubleshooting, backing up, and operating the SAT-SA supervisory analytics platform inside an air-gapped NCIIPC installation.

## 2. Standard Operating Procedures (SOPs)

### SOP-01: Ingesting Periodic CSE Submissions
1. Receive official CSV/JSON export media from the Critical Sector Entity.
2. In the SAT-SA Console, navigate to **Submissions & Quality**.
3. Select the target entity (e.g. `CSE-04: National Rail Logistics`) and reporting cycle (e.g. `2026-Q3`).
4. Upload submission files (`alerts.csv`, `cases.csv`, `assets.csv`, `investigation_steps.csv`, `escalations.csv`, `telemetry_coverage.csv`).
5. Review the automated Data Quality summary:
   - Verify `DQ-001` through `DQ-012` status.
   - Confirm quarantined row count is acceptable.
6. Click **Approve & Run Supervisory Analytics**.

### SOP-02: Handling Ingestion Errors & Data Quarantine
1. If a batch contains rows failing referential integrity (e.g. alert references an unregistered `asset_id`), SAT-SA automatically routes those records to the quarantine log (`DQ-008`).
2. Navigate to **Data Quality Log** and export the quarantine audit CSV.
3. Transmit the quarantine audit summary back to the CSE security officer requesting corrective resubmission.
4. *Do NOT edit the immutable raw uploaded file in place.* All corrections must arrive as an incremented version (e.g., `v2`).

### SOP-03: Running Sector Peer Benchmarking
1. Once all CSE submissions for a quarter are ingested, navigate to **Analytics & Benchmarks**.
2. Select **Run Sector Aggregations**.
3. The platform computes non-parametric statistical metrics across peer cohorts:
   - Median alert closure duration ($T_{closure}$)
   - Critical alert escalation frequency
   - Case-to-alert linkage ratio
   - Asset coverage density
4. Verify updated sector peer distributions before publishing the quarterly entity leaderboard.

### SOP-04: Database Backup & Cryptographic Verification
1. To perform a point-in-time backup of the SQLite database:
   ```bash
   sqlite3 data/sat_sa.db ".backup data/backups/sat_sa_backup_$(date +%Y%m%d_%H%M%S).db"
   ```
2. Compute and log the SHA-256 hash of the backup file:
   ```bash
   sha256sum data/backups/sat_sa_backup_*.db >> data/backups/backup_integrity.log
   ```
3. Run the automated audit verification script to confirm zero tampering:
   ```bash
   python -m pytest tests/unit/test_audit.py -k test_audit_chain_integrity
   ```

### SOP-05: Incident Handling & Emergency Rollback
- If an analytics rule requires modification due to revised national directives, update the rule configuration file and increment its version (e.g., `escalation-v1.3` $\rightarrow$ `escalation-v1.4`).
- Old findings retain their historic rule version links and evidence citations, guaranteeing complete historical reproducibility.
