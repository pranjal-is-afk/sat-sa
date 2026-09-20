# 04. User Requirements Document (URD)

## 1. User Personas

### Persona 1: Vikram — Senior Supervisory Examiner
- **Role**: Leads technical deep dives into CSE operational data submissions.
- **Goals**: Rapidly pinpoint suspicious operational patterns; examine supporting alert, case, and asset evidence; document findings for regulatory follow-up.
- **Pain Points**: Overwhelmed by massive CSV spreadsheets; lacks tools to detect copy-pasted investigation notes across thousands of incidents; cannot easily see what records are missing.
- **Needs**: An intelligent review queue ordered by risk; instant drill-down from finding to raw logs; one-click disposition logging.

### Persona 2: Priya — Chief Supervisory Officer / Assessment Director
- **Role**: Oversees cross-sector cyber resilience evaluations and reports to national leadership.
- **Goals**: Compare resilience across critical infrastructure sectors (Power vs. Banking vs. Telecom); identify entities falling behind peer benchmarks; generate executive oversight briefings.
- **Pain Points**: Misled by self-reported compliance scores and superficial SLA dashboards.
- **Needs**: Cross-entity ranking leaderboard with transparent score breakdown; peer group comparison distribution charts; exportable executive audit packages.

### Persona 3: Ankit — Data & Enclave Administrator
- **Role**: Ingests periodic submission packages inside the air-gapped operations center.
- **Goals**: Verify file hashes, run schema validations, quarantine malformed rows, and trigger analytics runs.
- **Pain Points**: Fragile ingestion pipelines that crash on malformed dates or missing columns.
- **Needs**: Clear data-quality dashboards; automated referential integrity checking; isolated quarantine log.

## 2. User Requirements by Persona

| Requirement ID | Persona | Requirement Description | Acceptance Criteria |
|---|---|---|---|
| **UR-01** | Vikram | View a prioritized queue of supervisory findings | Queue displays severity, finding title, entity, confidence, and date |
| **UR-02** | Vikram | Drill into a finding to inspect linked alerts, cases, assets, and escalations | Detailed evidence table with exact IDs, fields, and values |
| **UR-03** | Vikram | View a chronological timeline of how an alert was handled | Visual lifecycle showing alert creation, case open, notes, closure |
| **UR-04** | Vikram | Record formal review disposition with comments | Form with disposition options and mandatory notes; writes to audit log |
| **UR-05** | Priya | View an entity risk leaderboard with score contributors | Entity list sorted by risk score; displays percentage contribution bar |
| **UR-06** | Priya | Compare a CSE's metrics against sector peer group | Peer distribution chart showing median, 25th, 75th percentiles |
| **UR-07** | Priya | Export an evidence-backed supervisory assessment report | Generates structured HTML/PDF/JSON package with full audit trail |
| **UR-08** | Ankit | Upload submission batches and view validation diagnostics | Progress bar, schema checks, count of clean vs. quarantined rows |
| **UR-09** | Ankit | Verify raw file integrity using SHA-256 hashes | Displays uploaded file hash and confirms cryptographic match |
