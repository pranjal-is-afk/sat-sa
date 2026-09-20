# 19. Requirements Traceability Matrix (RTM)

## 1. Traceability Mapping
This matrix maps every requirement from the official NCIIPC / SIH26157 Problem Statement to the corresponding system feature, architecture module, test evidence, and live demo artifact.

| SIH Requirement | Product Capability | Design Artifact | Code Implementation | Verification Test | Demo Evidence |
|---|---|---|---|---|---|
| **Ingest data from multiple CSEs** | Submission Manager | `DRD`, `SRD` | `backend/app/routers/submissions.py` | `test_ingestion_pipeline.py` | Batch CSV upload for 10 entities |
| **Support CSV and JSON formats** | Ingestion Engine | `DRD`, `API Spec` | `backend/app/services/ingestion_service.py` | `test_parsers.py` | Upload of CSV and JSON records |
| **Validate schema and quality** | Data Quality Checker | `DRD`, `SRD` | `backend/app/services/validation_service.py` | `test_data_quality.py` | Live display of DQ-001 - DQ-012 issues |
| **Detect execution gaps** | Deterministic Rule Engine| `AMD`, `LLD` | `analytics/rules/critical_alert_no_escalation.py` | `test_rules.py` | Finding card `F-ESC-00021` |
| **Detect fast high-severity closures**| Fast-Closure Rule | `AMD`, `HLD` | `analytics/rules/high_severity_fast_closure.py` | `test_fast_closure.py` | Finding card `F-INV-002` (<5 mins) |
| **Detect negative space** | Negative-Space Engine | `AMD`, `PRD` | `analytics/rules/critical_asset_missing_telemetry.py` | `test_negative_space.py` | Silent asset `AST-104` (21 days quiet) |
| **Detect boilerplate notes** | Local NLP Similarity | `AMD`, `Model Card`| `analytics/rules/repetitive_investigation_notes.py` | `test_nlp_similarity.py` | TF-IDF 93% similarity flag |
| **Peer benchmarking** | Peer Comparison Dashboard| `AMD`, `UXD` | `backend/app/routers/peer_groups.py` | `test_benchmarking.py` | Sector distribution & radar chart |
| **Entity risk indicators** | Decomposed Risk Scorer | `AMD`, `PRD` | `analytics/scoring/entity_risk_scorer.py` | `test_scoring.py` | Entity leaderboard with score breakdown |
| **Prioritize manual review** | Prioritized Review Queue | `UXD`, `URD` | `analytics/scoring/case_prioritizer.py` | `test_queue.py` | Interactive triage review queue |
| **Explainable findings** | Finding Detail View | `UXD`, `API Spec` | `backend/app/routers/findings.py` | `test_explainability.py` | Plain-language rationale & evidence table |
| **Auditability & lineage** | Cryptographic Audit Store| `SSD`, `LLD` | `backend/app/services/audit_service.py` | `test_audit.py` | SHA-256 chained audit verification |
| **Offline air-gap operation** | Containerized Local Stack| `DGD`, `SSD` | `infrastructure/docker/Dockerfile` | `test_airgap.py` | Full offline execution on localhost |
| **Human-in-the-loop decisions** | Review Disposition Form | `UXD`, `PRD` | `backend/app/routers/findings.py` | `test_dispositions.py` | Recorded reviewer notes in audit log |
| **Supervisory reporting** | Report Export Engine | `PRD`, `API Spec` | `backend/app/services/report_service.py` | `test_reporting.py` | Downloadable Executive Report HTML/JSON |
