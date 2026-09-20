# 03. Product Requirements Document (PRD)

## 1. Product Overview & Vision
SAT-SA enables NCIIPC supervisors to move from broad periodic SOC data submissions to a prioritized, explainable, evidence-backed review queue, while retaining complete human control over supervisory judgement.

## 2. Product Goals & Non-Goals
### Primary Goals
- Ingest periodic structured data submissions from multiple CSEs in CSV and JSON formats.
- Detect hidden execution gaps (uninvestigated alerts, missing escalations, copy-paste narratives).
- Uncover negative space (silent critical assets, missing expected alert streams).
- Generate risk-adjusted peer benchmarks across sector profiles.
- Compute transparent, decomposed supervisory prioritization scores.
- Produce a prioritized manual-review queue for examiners.
- Provide end-to-end evidence drill-down and cryptographic audit logging.
- Run 100% offline in air-gapped enclaves.

### Non-Goals
- Real-time continuous log ingestion or packet sniffing.
- SIEM or SOAR replacement.
- Autonomous remediation or automated blocking actions against CSEs.
- Dependence on cloud services or external LLM APIs (e.g. OpenAI, Claude, Gemini).

## 3. User Roles
- **Supervisory Examiner**: Triage findings, inspect evidence timelines, record dispositions.
- **Lead Supervisor**: Review portfolio leaderboard, approve reports, configure peer groups.
- **Data Administrator**: Upload submission batches, validate schemas, review data-quality reports.
- **System Administrator**: Manage enclave deployment, backup/restore, user accounts.
- **Auditor**: Inspect tamper-evident audit trails and cryptographic hashes.

## 4. Functional Modules
```
┌─────────────────────────────────────────────────────────┐
│                    SAT-SA Product Modules               │
├───────────────────┬───────────────────┬─────────────────┤
│ 1. Data Intake    │ 2. Data Quality   │ 3. Normalizer   │
│ Multi-file upload │ DQ-001 - DQ-012   │ Canonical Model │
├───────────────────┼───────────────────┼─────────────────┤
│ 4. Analytics      │ 5. Prioritization │ 6. Review Queue │
│ Rules, Stats, NLP │ Decomposed Score  │ Prioritized Triage│
├───────────────────┼───────────────────┼─────────────────┤
│ 7. Drill-Down     │ 8. Audit Layer    │ 9. Reporting    │
│ Record Evidence   │ SHA-256 Chaining  │ PDF/HTML Packs  │
└───────────────────┴───────────────────┴─────────────────┘
```

## 5. Core Feature Requirements
### Module 1: Data Intake & Upload
- Multi-file drag-and-drop ingestion for `alerts.csv`, `cases.csv`, `investigation_steps.csv`, `escalations.csv`, `assets.csv`, `telemetry_coverage.csv`, `remediations.csv`.
- Automatic calculation of file SHA-256 checksums and immutable storage of raw source submissions.

### Module 2: Data Quality & Normalization
- Validation against schemas and integrity checks:
  - `DQ-001`: Declared CSE entity identifier present.
  - `DQ-002`: Unique alert IDs per submission.
  - `DQ-003`: `closed_at` must not precede `created_at`.
  - `DQ-004`: `acknowledged_at` must not precede `created_at`.
  - `DQ-005`: Referential integrity: Cases linked to alerts must resolve.
  - `DQ-006`: Referential integrity: Escalations linked to cases must resolve.
  - `DQ-007`: Valid severities (`Critical`, `High`, `Medium`, `Low`).
  - `DQ-008`: Assets referenced in alerts must resolve to inventory.
  - `DQ-009`: Deduplication and versioning.
  - `DQ-010`: Quarantine log for malformed records without halting batch processing.

### Module 3: Supervisory Analytics Engine
- **Rule R-ESC-001 (Missing Escalation)**: Flags Critical alerts on Critical assets lacking escalation records.
- **Rule R-INV-002 (Unusually Fast Closure)**: Flags High/Critical cases closed under threshold or below peer 5th percentile with low evidence count.
- **Rule R-INV-001 (Superficial Investigation)**: Flags acknowledged alerts closed without investigative steps, evidence items, or root causes.
- **Rule R-REM-001 (Repeated Alerts Without Remediation)**: Groups alerts by asset and detection signature; flags recurring alerts where no remediation plan exists.
- **Rule R-INV-003 (Repetitive Investigation Narratives)**: Uses local TF-IDF cosine similarity matrix to flag cases sharing boilerplate text across different assets.
- **Rule R-NEG-001 (Negative Space - Missing Telemetry)**: Flags critical inventory assets with zero alert activity or telemetry records for over 14 days.
- **Rule R-SEQ-001 (Workflow Sequence Violations)**: Identifies illogical lifecycle sequences (e.g. case closed before investigation began).
- **Rule R-GAM-001 (Metric Gaming Patterns)**: Flags unnatural closure spikes right before SLA cutoffs or end-of-month reporting dates.

### Module 4: Entity Risk Scoring & Prioritization
- Decomposed formula:
  $$R_{entity} = w_D D + w_I I + w_E E + w_N N + w_P P + w_Q Q$$
  where $w_D = 0.20$, $w_I = 0.25$, $w_E = 0.25$, $w_N = 0.15$, $w_P = 0.10$, $w_Q = 0.05$.
- Breakdown display: The UI explicitly shows the exact percentage attribution of each risk dimension.

### Module 5: Human-in-the-Loop Review & Audit
- Reviewer disposition workflow: `Confirmed`, `Not Substantiated`, `False Positive`, `Needs More Evidence`, `Escalated`, `Accepted Risk`, `Remediation Required`.
- Immutable append-only audit trail logging user, timestamp, previous status, new status, rationale, and SHA-256 hash chaining.

## 6. Acceptance Criteria
- [x] Ingests full submission files in under 10 seconds for 100,000 demo records.
- [x] Correctly identifies 100% of injected ground-truth conditions across all 10 synthetic CSE profiles.
- [x] Every generated finding provides exact record links, timestamps, and plain-language explanation.
- [x] System boots, executes, and exports reports with network interface disabled.
