# 01. Business Requirements Document (BRD)

## 1. Document Control
- **Document Title**: Business Requirements Document: SAT-SA
- **Target Organization**: NCIIPC / NTRO Context
- **Version**: 1.0.0
- **Classification**: Internal / Restricted Evaluation

## 2. Purpose
This document defines the strategic and operational business requirements for the Supervisory Analytics Tool for SOC Assessment (SAT-SA). It articulates the supervisory challenges facing NCIIPC, establishes project objectives, defines business scope and boundaries, and outlines testable business success criteria.

## 3. Background & Operational Environment
Under statutory guidelines, NCIIPC assesses the cyber resilience and operational controls of Critical Sector Entities (CSEs). CSEs operate Security Operations Centers (SOCs) responsible for detecting, triaging, investigating, and escalating cyber threats against critical infrastructure.

In current workflows, NCIIPC supervisors review periodic submissions of SOC operational evidence (alerts, incident records, case notes, escalation chains, asset lists). While these records provide deep insight into operational behavior, human examiners face severe scalability constraints when attempting to manually inspect tens of thousands of records across dozens of entities.

## 4. Business Problem
Conventional oversight mechanisms fail to reveal operational deficiencies:
1. **Self-Assessment Questionnaires & Audits**: Organizations report comprehensive compliance on paper, yet actual execution may be dysfunctional.
2. **KPI Dashboards (Mean Time to Detect / Close)**: High alert-closure compliance can be gamed by rapidly resolving high-severity alerts without meaningful investigation.
3. **Manual Sampling Blindspots**: Examiners can inspect only 1–3% of submitted records. Random sampling routinely misses high-consequence execution breakdowns and negative-space anomalies.
4. **Lack of Cross-Entity Peer Benchmarks**: Examiners lack standardized statistical baselines to determine whether an entity's 6-minute closure time is efficient or suspiciously superficial compared to peers in the same sector.

## 5. Stakeholders
- **Primary Users**: NCIIPC Supervisory Examiners (carry out evidence inspections and case reviews).
- **Secondary Users**: Lead Supervisors / Assessment Directors (portfolio overview, cross-sector benchmarking, formal report generation).
- **Supporting Roles**: Data Administrators (ingestion, schema validation), System Administrators (air-gap enclave maintenance), Enclave Auditors (traceability audits).
- **Assessed Parties**: Critical Sector Entities (CSEs submitting periodic operational logs).

## 6. Business Objectives
- **BO-1**: Reduce examiner effort required to identify high-priority supervisory findings by at least 70%.
- **BO-2**: Increase the detection rate of hidden execution gaps (uninvestigated critical alerts, unescalated high-severity cases).
- **BO-3**: Uncover negative space (silent critical assets, missing telemetry, absence of expected threat categories).
- **BO-4**: Establish transparent, risk-adjusted peer benchmarking across comparable sector profiles.
- **BO-5**: Guarantee 100% data lineage and auditability from any high-level finding down to raw submission records.
- **BO-6**: Ensure 100% air-gapped operability within isolated NCIIPC server enclaves without cloud reliance.

## 7. Business Scope
- Periodic structured batch ingestion (CSV, JSON) for alerts, cases, investigation steps, escalations, remediations, assets, and telemetry coverage.
- Explainable deterministic rule checks, statistical peer comparisons, and offline NLP text-similarity checks.
- Decomposed entity risk ranking and prioritized manual-review queuing.
- Interactive human-in-the-loop review dispositioning and evidence-backed supervisory report generation.

## 8. Out of Scope
- Real-time packet capture, live SIEM continuous ingestion, or automated network containment.
- Replacing the operational SOC or taking unilateral blocking actions.
- External cloud-hosted AI APIs (OpenAI, Gemini, Claude) or internet-dependent threat feeds.

## 9. Business Requirements Matrix
| ID | Business Requirement | Priority | Target Verification |
|---|---|---|---|
| **BR-01** | The platform shall identify CSEs requiring urgent supervisory attention based on operational evidence | Critical | Entity ranking leaderboard with decomposed score contributors |
| **BR-02** | The platform shall prioritize individual alerts, cases, and assets into an actionable review queue | Critical | Prioritized review queue sorted by $P_{case}$ |
| **BR-03** | The platform shall detect execution gaps between reported capabilities and operational evidence | Critical | Detection of fast closures, missing escalations, boilerplate notes |
| **BR-04** | The platform shall detect negative space (unmonitored critical assets, missing expected alert streams) | Critical | $C_{asset} = 0$ alerts and missing category analysis |
| **BR-05** | The platform shall preserve human supervisor authority over all final evaluations | High | Interactive review disposition workflows |
| **BR-06** | The platform shall provide explainable, evidence-backed findings citing raw record IDs and rule versions | Critical | Finding detail cards with structured evidence tables |
| **BR-07** | The platform shall function completely within an isolated, air-gapped environment | Critical | Full system boot and execution with zero network access |
| **BR-08** | The platform shall support peer-group comparisons controlling for entity size, asset count, and sector | High | Sector-adjusted statistical distribution benchmarks |

## 10. Success Metrics
- **Top-10 / Top-50 Recall**: Over 90% of ground-truth operational weaknesses surfaced in the top 50 prioritized cases.
- **Evidence Lineage**: 100% of generated findings link directly to valid submitted record keys.
- **Offline Integrity**: Zero runtime dependency errors when disconnected from the Internet.
- **Examiner Confidence**: Transparent scoring explanations rated clear and actionable in evaluation trials.
