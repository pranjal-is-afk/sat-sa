# Changelog

All notable changes to the SAT-SA supervisory analytics platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-08
### Added
- **Data Ingestion & Normalization**: CSV/JSON parsers with SHA-256 integrity validation, DQ-001 through DQ-012 quality rules, and quarantine store.
- **Explainable Supervisory Analytics Engine**:
  - Deterministic rules: `R-ESC-001` (Critical alert missing escalation), `R-INV-002` (High-severity alert fast closure), `R-INV-001` (Alert without meaningful investigation), `R-REM-001` (Repeated alerts without remediation).
  - Negative-space analytics: `R-NEG-001` (Critical asset missing monitoring evidence / telemetry).
  - NLP similarity analytics: `R-INV-003` (TF-IDF cosine similarity for template/boilerplate investigation detection).
  - Robust statistical peer benchmarking (IQR, median, percentile rank, rate normalization).
  - Workflow sequence & temporal anomaly checks (timestamp inversions, metric gaming).
  - Unsupervised multivariate outlier detection using local Isolation Forest.
- **Decomposed Risk Scoring**: Transparent entity risk formula $R_{entity} = w_D D + w_I I + w_E E + w_N N + w_P P + w_Q Q$ with percentage contributor breakdown.
- **Human-in-the-Loop Review Queue**: Prioritized case triage and interactive disposition recording (Confirmed, Not Substantiated, False Positive, Needs More Evidence, Remediation Required).
- **Audit Layer**: Append-only audit events with cryptographic SHA-256 hash chaining.
- **Reporting Engine**: One-click generation of supervisory assessment reports with complete evidence drill-down.
- **Synthetic Ground-Truth Generator**: 10 distinct CSE operational profiles with verified ground truth labels.
- **Zero-Dependency Web UI**: Modern, responsive, air-gapped supervisory console.
- **Comprehensive Documentation Suite**: 23 documentation files (`docs/00` to `docs/22`).
