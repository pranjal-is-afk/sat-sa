# 06. System Requirements Document (SRD / SRS)

## 1. System Purpose & Scope
This Software Requirements Specification defines the precise functional, non-functional, interface, security, and data requirements for the SAT-SA system.

## 2. Functional Requirements (FR)

| Requirement ID | Module | Description | Verification Method |
|---|---|---|---|
| **FR-001** | Ingestion | Ingest periodic CSV and JSON files containing SOC operational data | Automated Parser Test |
| **FR-002** | Ingestion | Support submissions across multiple distinct CSEs and reporting periods | Integration Test |
| **FR-003** | Ingestion | Validate required columns and data formats prior to canonical storage | Schema Validator Test |
| **FR-004** | Ingestion | Compute and store file SHA-256 hash, upload timestamp, and uploader identity | Cryptographic Hash Test |
| **FR-005** | Normalization | Normalize alerts, cases, investigation steps, escalations, remediations, and assets into a canonical model | Normalizer Unit Test |
| **FR-006** | Analytics | Detect critical alerts on critical assets lacking escalation records (`R-ESC-001`) | Rule Logic Test |
| **FR-007** | Analytics | Detect high/critical severity cases closed unusually fast relative to peer baselines (`R-INV-002`) | Percentile Rule Test |
| **FR-008** | Analytics | Detect alerts closed without investigative workflow steps or evidence items (`R-INV-001`) | Completeness Test |
| **FR-009** | Analytics | Detect recurring alerts affecting the same asset without root-cause remediation (`R-REM-001`) | Recurrence Math Test |
| **FR-010** | Analytics | Detect boilerplate and copy-pasted investigation narratives across cases (`R-INV-003`) | TF-IDF Cosine Test |
| **FR-011** | Analytics | Detect critical assets with missing or abnormally low monitoring evidence (`R-NEG-001`) | Negative Space Test |
| **FR-012** | Analytics | Perform risk-adjusted peer comparison controlling for asset volume and sector | Benchmark Test |
| **FR-013** | Scoring | Compute transparent decomposed entity supervisory risk score: $R_{entity} = \sum w_i S_i$ | Scoring Unit Test |
| **FR-014** | Triage | Prioritize review queue by risk, evidence strength, impact, and novelty | Ranking Algorithm Test |
| **FR-015** | Explainability| Include plain-language reason, exact record IDs, and comparison baselines with each finding | Contract Test |
| **FR-016** | Review | Allow supervisors to record formal dispositions with notes and timestamps | Review Flow Test |
| **FR-017** | Reporting | Generate downloadable, evidence-backed supervisory assessment reports (HTML/PDF/JSON) | Report Generator Test |
| **FR-018** | Audit | Retain immutable append-only audit records with SHA-256 state chaining | Audit Chaining Test |

## 3. Non-Functional Requirements (NFR)

| Requirement ID | Category | Requirement Specification |
|---|---|---|
| **NFR-001** | Air-Gap Strictness | System shall operate 100% offline with zero external network egress or API dependencies |
| **NFR-002** | Hardware Independence | Minimum demo requirements: 4 CPU cores, 8 GB RAM; no dedicated GPU required |
| **NFR-003** | Ingestion Throughput | Process 100,000+ alert records from CSV in under 30 seconds on standard commodity hardware |
| **NFR-004** | Latency | Return filtered findings and dashboard views in < 500ms |
| **NFR-005** | Security & RBAC | Enforce role-based access control across Supervisor, Lead Supervisor, Admin, and Auditor |
| **NFR-006** | Data Integrity | Maintain immutable raw submissions and 100% cryptographic trace link between findings and source rows |
| **NFR-007** | Injection Prevention | Sanitize CSV inputs against formula injection and enforce 100% parameterized SQL queries |
| **NFR-008** | Audit Chaining | Ensure every audit event includes a SHA-256 hash of its contents and the previous event hash |
| **NFR-009** | Zero CDN Reliance | All web assets (CSS, JS, fonts, SVG icons) must be locally vendored and served without remote CDNs |
