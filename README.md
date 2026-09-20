# SAT-SA: Supervisory Analytics Tool for SOC Assessment

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Deployment](https://img.shields.io/badge/deployment-Air--Gapped%20Offline-orange.svg)](docs/16-deployment-installation-guide.md)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](requirements.txt)

> **Operational Evidence over Reported Compliance**  
> An air-gapped, explainable supervisory intelligence platform that transforms periodic SOC alert and case-management submissions into evidence-backed entity risk indicators and prioritized manual-review queues.

---

## 1. Executive Context (SIH26157 — NTRO / NCIIPC)
NCIIPC assesses the cyber resilience of **Critical Sector Entities (CSEs)** across power grids, telecommunications, banking, transport, nuclear, and defense sectors. Today, NCIIPC examiners manually inspect samples of SOC operational data. Traditional compliance reports and high-level KPI dashboards can conceal significant operational vulnerabilities:
- High alert-closure compliance hiding critical alerts closed in minutes without analysis.
- Generic, boilerplate investigation notes copy-pasted across incidents.
- Critical incidents quietly resolved without required escalation to authorities.
- Chronic alert repetition on critical systems with zero root-cause remediation.
- **Negative Space**: Total absence of security telemetry or alert activity on declared critical assets.

**SAT-SA is NOT a SIEM, real-time SOC, or continuous packet analyzer.** It is an **offline supervisory decision-support platform** designed to scale manual supervisory review across large datasets without replacing human judgement.

```
┌─────────────────────────────────────────────────────────┐
│              NCIIPC-Controlled Air-Gapped Enclave       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Supervisory Console & Web Dashboard       │  │
│  │    Portfolio Leaderboard • Findings • Drill-Down  │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │ HTTPS / Local Network      │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │                Application Backend                │  │
│  │       FastAPI • Local RBAC • Ingestion Engine     │  │
│  └─────────────┬─────────────────────────┬───────────┘  │
│                │                         │              │
│  ┌─────────────▼──────────┐ ┌────────────▼───────────┐  │
│  │ Data Intake & Quality  │ │   Supervisory Engine   │  │
│  │ Schema • Hashes • DQ   │ │ Rules • Stats • NLP ML │  │
│  └─────────────┬──────────┘ └────────────┬───────────┘  │
│                │                         │              │
│  ┌─────────────▼─────────────────────────▼───────────┐  │
│  │                   Local Data Store                │  │
│  │   SQLite WAL • Canonical Tables • SHA-256 Audit   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│     No Internet • No Cloud • Zero Remote Telemetry      │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Core Capabilities

### A. Data Ingestion & Quality Validation
- Ingests structured periodic submissions in **CSV** or **JSON** for:
  - `alerts`, `cases`, `investigation_steps`, `escalations`, `assets`, `telemetry_coverage`, `remediations`.
- Enforces strict data-quality rules (`DQ-001` through `DQ-012`): schema conformance, referential integrity, logical timestamps, and malformed row quarantining.
- Calculates and stores **SHA-256 hashes** for 100% data lineage and integrity verification.

### B. Hybrid Supervisory Analytics
1. **Deterministic Rule Engine**:
   - `R-ESC-001`: Critical Alert Missing Mandatory Escalation.
   - `R-INV-002`: High-Severity Alert Closed Unusually Fast (< peer 5th percentile).
   - `R-INV-001`: Alert Acknowledged but Closed Without Investigation Evidence ($Q_{investigation}$).
   - `R-REM-001`: Repeated Alerts on Same Asset Without Remediation ($R_{repeat}$).
   - `R-SEQ-001`: Workflow Sequence & Temporal Violations (closures before investigation, post-closure escalation).
   - `R-GAM-001`: SLA & Metric Gaming Patterns (suspicious closure bursts, end-of-month spikes).
2. **Negative-Space Detection**:
   - `R-NEG-001`: Identifies critical assets expected to be monitored that produce zero telemetry or alert activity ($C_{asset} = 0$).
   - Missing expected alert categories based on business service profile.
3. **Local NLP & Text Similarity**:
   - `R-INV-003`: Offline TF-IDF vectorization and cosine similarity matrix detection for repetitive, boilerplate investigation narratives.
4. **Statistical Peer Benchmarking**:
   - Robust metrics (Median, IQR, Median Absolute Deviation, Percentile Rank).
   - Rate-normalized comparison controlling for asset count, criticality, and reporting days.
5. **Unsupervised Anomaly Discovery**:
   - Embedded scikit-learn Isolation Forest detecting multidimensional behavioral outliers.

### C. Transparent Entity Scoring & Queue Prioritization
- **Decomposed Entity Score**:
  $$R_{entity} = w_D D + w_I I + w_E E + w_N N + w_P P + w_Q Q$$
  Never outputs a black-box number; always displays exact contributor percentages (e.g. 31% escalation gaps, 24% repeated alerts, 18% fast closures).
- **Prioritized Review Queue**:
  $$P_{case} = \text{Severity} \times \text{Evidence Strength} \times \text{Impact} \times \text{Novelty}$$
  Concentrates examiner attention on highest-value inspection targets.

### D. Human-in-the-Loop Explainability & Audit Trail
- Every finding specifies: *Finding ID, Category, Severity, Confidence, Plain-language Rationale, Exact Record References, Baseline Comparison, Rule Version, and Recommended Supervisory Action*.
- Interactive supervisor dispositions: `Confirmed`, `Not Substantiated`, `False Positive`, `Needs More Evidence`, `Escalated`, `Accepted Risk`, `Remediation Required`.
- Immutable append-only audit trail with SHA-256 hash chaining.

---

## 3. Quickstart Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.11, 3.12, 3.14)
- Web browser (Edge, Chrome, Firefox)
- Fully functional in air-gapped / offline environments.

### 1-Command Installation & Demo Launch
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed synthetic ground-truth data, initialize SQLite database, and launch server
python run.py --seed --port 8000
```

Open your browser at:
```
http://127.0.0.1:8000
```

### Preloaded Synthetic Ground-Truth Profiles
The platform includes 10 realistic CSE profiles with verified injected supervisory conditions:
- **CSE-01**: Healthy baseline operations (Power Grid).
- **CSE-02**: High-volume banking SOC with normal operational parameters.
- **CSE-03**: Telecom provider with Critical Alerts missing mandatory escalation (`R-ESC-001`).
- **CSE-04**: Transport authority with high-severity alerts closed in < 5 minutes (`R-INV-002`).
- **CSE-05**: Defense contractor with copy-paste boilerplate investigation notes (`R-INV-003`).
- **CSE-06**: Nuclear facility with chronic repeat alerts on critical assets without remediation (`R-REM-001`).
- **CSE-07**: Petroleum pipeline with critical assets producing zero telemetry / negative space (`R-NEG-001`).
- **CSE-08**: Water authority with suspiciously low alert activity relative to peers.
- **CSE-09**: Smart grid SOC with schema errors and broken relational references (`DQ-005`).
- **CSE-10**: Mixed complex critical infrastructure scenario with multiple overlapping gaps.

---

## 4. Verification & Testing

Run all unit, integration, security, and benchmark validation suites:
```bash
# Run complete test suite
python -m pytest tests/ -v

# Run ground-truth validation benchmark (Precision, Recall, Top-k Recall)
python -m pytest tests/validation/ -v

# Run air-gap & security verification tests
python -m pytest tests/security/ -v
```

---

## 5. Repository & Documentation Structure

```
sat-sa/
├── README.md                               # This documentation
├── LICENSE                                 # MIT License
├── SECURITY.md                             # Air-gap & security guidelines
├── CONTRIBUTING.md                         # Developer contribution guidelines
├── CHANGELOG.md                            # Release history
├── requirements.txt                        # Local dependencies
├── run.py                                  # CLI runner and seeder
│
├── docs/                                   # Complete 23-document specification set
│   ├── 00-executive-summary.md             # High-level executive briefing
│   ├── 01-brd-business-requirements.md     # Business requirements document
│   ├── 02-mrd-market-requirements.md       # Market & domain analysis
│   ├── 03-prd-product-requirements.md      # Complete product specification
│   ├── 04-urd-user-requirements.md         # User requirements document
│   ├── 05-user-flows.md                    # Core user journeys & workflow diagrams
│   ├── 06-srd-system-requirements.md       # Testable functional/non-functional specs
│   ├── 07-drd-data-requirements.md         # Data dictionary, schemas & lineage
│   ├── 08-analytics-model-design.md        # Analytics equations, rules & scoring
│   ├── 09-architecture-hld.md              # 2-page executive + deep architecture
│   ├── 10-low-level-design.md              # Module-by-module technical design
│   ├── 11-api-specification.md             # REST API endpoint contracts
│   ├── 12-database-schema.md               # SQLite/PostgreSQL DDL & ER diagram
│   ├── 13-ui-ux-specification.md           # Screen layouts & interaction model
│   ├── 14-security-threat-model.md         # Threat analysis & air-gap mitigations
│   ├── 15-ai-governance-model-card.md      # ML model cards & explainability controls
│   ├── 16-deployment-installation-guide.md # Air-gapped deployment runbook
│   ├── 17-operational-runbook.md           # Administrative maintenance guide
│   ├── 18-testing-validation-plan.md       # V&V test matrix & ground-truth metrics
│   ├── 19-requirements-traceability-matrix.md # Problem statement requirement mapping
│   ├── 20-release-change-management.md     # Versioning & model update policy
│   ├── 21-demo-script.md                   # 2-minute evaluation demo walk-through
│   └── 22-limitations-roadmap.md           # Known constraints & future phases
│
├── data/
│   ├── schemas/                            # JSON schemas for canonical entities
│   ├── data-dictionary/                    # Data dictionary definitions
│   ├── data-quality-rules/                 # Rules DQ-001 through DQ-012
│   ├── synthetic-data-generation/          # 10 CSE synthetic profile generator
│   └── sample/                             # Pre-generated sample CSV files
│
├── analytics/                              # Hybrid supervisory analytics engine
│   ├── engine.py                           # Analytics orchestrator
│   ├── rules/                              # Deterministic & negative space rules
│   ├── scoring/                            # Decomposed risk & triage scoring
│   └── anomaly/                            # Scikit-learn Isolation Forest
│
├── backend/
│   ├── app/
│   │   ├── main.py                         # FastAPI web service
│   │   ├── config.py                       # Configuration & offline flags
│   │   ├── database/                       # Database setup & schema DDL
│   │   ├── models/                         # Pydantic schemas
│   │   ├── services/                       # Ingestion, audit, reporting services
│   │   └── routers/                        # Endpoints: entities, findings, submissions...
│
├── frontend/                               # Zero-CDN, responsive supervisory UI
│   ├── index.html                          # Single-page executive web console
│   ├── css/style.css                       # Modern dark/light cyber-defense styling
│   └── js/app.js                           # Interactive filtering, drilldown, charts
│
├── infrastructure/
│   ├── docker/                             # Dockerfile & compose configuration
│   └── scripts/                            # Air-gap packaging & export scripts
│
└── tests/
    ├── unit/                               # Parser, rule & scoring unit tests
    ├── integration/                        # End-to-end API & ingestion workflows
    ├── security/                           # Input validation, injection defense
    └── validation/                         # Precision, Recall & Top-k validation
```

---

## 6. Air-Gapped Deployment Checklist

- [x] **Zero Remote Network Egress**: Confirmed with firewall isolation test.
- [x] **Zero CDN Dependencies**: All CSS/JS, fonts, and icons vendored locally.
- [x] **Zero External AI / LLM APIs**: All analytics run deterministic Python code, SciPy, NumPy, and scikit-learn.
- [x] **Immutable Raw Storage**: Uploaded files preserved with SHA-256 checksums.
- [x] **Cryptographic Audit Trail**: Every supervisor review action is logged with SHA-256 state chaining.
- [x] **Local Standalone Packaging**: Self-contained docker-compose and wheel distribution supported.
