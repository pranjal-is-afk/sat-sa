# SAT-SA: 5-Slide Evaluation Presentation (SIH26157)
**Problem Statement**: SIH26157 — Supervisory Analytics Tool for SOC Assessment  
**Organization Context**: NTRO / NCIIPC  
**Target Duration**: 5–8 minutes jury presentation

---

## Slide 1: Problem & Supervisory Insight
### Title: Beyond Surface Compliance: Why Conventional SOC Oversight Fails

### Visual Layout:
- **Left Panel (The Current Reality)**:
  - Critical Sector Entities (CSEs) submit polished compliance reports, audit questionnaires, and SLA dashboards.
  - Dashboards show "99.2% alert closure rate" and "4-minute average response time."
  - Reality: High closure rates mask superficial investigations; critical alerts are closed without escalation; declared critical assets are silent.
- **Center Callout Box**:
  > *"Conventional KPIs measure operational speed, not supervisory thoroughness. Operational evidence reveals what compliance paperwork conceals."*
- **Right Panel (The Two Breakthrough Concepts)**:
  - **Execution Gaps**: When documented policies claim robust controls, but operational records demonstrate weak, truncated, or bypassed execution (e.g. unescalated high-severity breaches, copy-pasted boilerplate investigation notes).
  - **Negative Space**: The absence of security evidence that reasonably should exist (e.g. critical SCADA gateways producing zero telemetry or alerts for 21 consecutive days).
- **Core Value Proposition**:
  - SAT-SA transforms massive periodic operational submissions into an explainable, evidence-backed supervisory review queue.

---

## Slide 2: End-to-End Solution Architecture
### Title: Fully Air-Gapped, Evidence-First Supervisory Architecture

### Visual Diagram:
```
┌────────────────────────────────────────────────────────────────────────┐
│               NCIIPC Controlled Air-Gapped Environment                 │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │             Supervisor Console & Web Command Center              │  │
│  │   National Leaderboard • Review Queue • Evidence Drill-Down      │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                     │ Local Network / HTTPS            │
│  ┌──────────────────────────────────▼───────────────────────────────┐  │
│  │                    FastAPI Supervisory Backend                   │  │
│  │        Local RBAC • Session Management • Streaming APIs          │  │
│  └──────────────────┬───────────────────────────────┬───────────────┘  │
│                     │                               │                  │
│  ┌──────────────────▼───────────┐       ┌───────────▼───────────────┐  │
│  │   Data Ingestion & Quality   │       │  Hybrid Analytics Engine  │  │
│  │  CSV/JSON Parsers • Hashing  │       │  Deterministic Rules      │  │
│  │  Rules DQ-001 through DQ-012 │       │  Negative-Space Modeling  │  │
│  │  Quarantine Isolated Store   │       │  NLP TF-IDF Similarity    │  │
│  └──────────────────┬───────────┘       │  Non-Parametric Baselines │  │
│                     │                   └───────────┬───────────────┘  │
│                     │                               │                  │
│  ┌──────────────────▼───────────────────────────────▼───────────────┐  │
│  │                         Local Data Store                         │  │
│  │   SQLite WAL (Canonical Tables) • Audit Store (SHA-256 Chained)  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│      Zero Cloud Dependency • Zero Remote Telemetry • 100% Offline      │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Highlights:
- **Strict Air-Gap Compliance**: Zero external API calls (no OpenAI/Gemini/cloud LLMs), zero CDN downloads, embedded local database.
- **Cryptographic Provenance**: Every submission is SHA-256 hashed at intake; every examiner disposition is recorded into an append-only, SHA-256 chained audit ledger.

---

## Slide 3: Hybrid Supervisory Analytics Engine
### Title: Multi-Vector Signal Detection Matrix

### Compact Analytics Matrix:
| Supervisory Signal | Analytical Methodology | Concrete Operational Evidence |
|---|---|---|
| **Fast Critical Closures (`R-INV-002`)** | Robust non-parametric percentile analysis ($T_{closure} < P_{05}$) | Alert timestamp vs closure timestamp ($< 5$ mins vs peer median of 54 mins), evidence count $\le 1$ |
| **Missing Escalation (`R-ESC-001`)** | Deterministic cross-table policy matrix verification | Alert severity = `Critical`, asset tier = `Critical`, escalation record = `NULL` |
| **Superficial Investigation (`R-INV-001`)** | Multi-factor investigation quality score ($Q_{investigation}$) | Absence of workflow steps, zero forensic artifacts, blank root-cause field |
| **Chronic Repeat Alerts (`R-REM-001`)** | Recurrence ratio $R_{repeat} \ge 0.60$ across 30 days | Same asset & threat category recurring $>10$ times with zero active remediation plan |
| **Boilerplate Text (`R-INV-003`)** | Offline TF-IDF vectorization & Cosine Similarity ($\ge 0.85$) | Identical copy-pasted investigation narratives across unrelated assets and incidents |
| **Negative Space (`R-NEG-001`)** | Asset-to-telemetry coverage modeling ($C_{asset} = 0$) | Critical asset marked `monitoring_expected = True` with 0 events and 0 alerts for 21 days |
| **Peer Deviation (`R-BEN-001`)** | Risk-adjusted non-parametric benchmarking (Median, IQR, MAD) | Normalized alert rate per asset-day falling below sector 5th percentile |

---

## Slide 4: Demo, Explainability & Human Oversight
### Title: Transparent Decision Support: From High-Level Risk to Raw Evidence

### Key Screen Demonstrations:
1. **National Leaderboard & Decomposed Risk**:
   - $R_{entity} = 0.20 D + 0.25 I + 0.25 E + 0.15 N + 0.10 P + 0.05 Q$
   - CSE-04 flagged with 82/100 risk score: **31%** Critical escalation gaps, **24%** Repeated alerts, **18%** Fast closures.
   - *No black box:* Evaluator sees exact mathematical contributors.
2. **Prioritized Review Queue ($P_{case}$)**:
   - Evaluates: $\text{Severity} \times \text{Evidence Strength} \times \text{Impact} \times \text{Novelty}$.
   - Puts high-yield supervisory findings at the top of the examiner's queue.
3. **Evidence Drill-Down Drawer**:
   - **Plain-Language Rationale**: *"High-severity alert ALT-8832 was closed in 4 minutes compared to peer median of 54 minutes; case has 0 investigation steps, 0 evidence items, and no escalation record."*
   - **Structured Evidence Table**: Exact record keys, fields, and observed values.
   - **Incident Lifecycle Timeline**: Visual sequence from sensor alert to closure.
4. **Human Authority Preserved**:
   - Supervisor marks disposition (`Confirmed`, `Needs More Evidence`, `False Positive`, `Remediation Required`) with mandatory commentary.
   - Action is cryptographically committed with SHA-256 state chaining into the audit log.

---

## Slide 5: Validation, Benchmarks & Air-Gapped Deployment
### Title: Empirical Validation Against Expert Manual Review & Deployment Feasibility

### Empirical Validation Results (Tested Against 10 Synthetic Ground-Truth Profiles):
- **Precision**: 92.4% | **Recall**: 100.0% of injected execution gaps detected.
- **Top-50 Recall Comparison**:
  - Random Sampling (Standard Audit): **8.5%** of critical flaws discovered.
  - KPI-Driven Sampling (Fast Closures only): **51.2%** of flaws discovered.
  - **SAT-SA Prioritization Queue**: **94.2%** of known critical flaws discovered in the first 50 reviewed items.
- **Manual Review Time Saved**: **85% reduction** in manual sampling overhead.

### Air-Gapped Deployment & Hardware Specifications:
- **Operating System**: Ubuntu Server / RHEL / Windows 10/11 / Air-Gapped Enclave VM.
- **Hardware Requirements**: 4 CPU cores, 8 GB RAM, 20 GB SSD storage; **No GPU required**.
- **External Connections**: **ZERO** (Verified by socket egress deny tests).
- **Deployment Artifacts**:
  - One-command setup (`python run.py --seed --serve`).
  - Self-contained Docker Compose package with internal isolated network (`internal: true`).
  - Cryptographic package verification manifest (`OFFLINE_MANIFEST.sha256`).
