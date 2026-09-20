# 02. Market & Domain Requirements Document (MRD)

## 1. Regulatory & Operational Domain Context
Critical Information Infrastructure (CII) protection mandates rigorous oversight of critical entities. Under national cybersecurity frameworks, designated entities in critical sectors (Power, Banking, Telecom, Transport, Government, Strategic Enterprises) must maintain functional Security Operations Centers (SOCs). 

Supervisory bodies such as NCIIPC conduct regular reviews to ensure these SOCs are not merely compliant on paper, but actively and effectively defending infrastructure against sophisticated adversaries.

## 2. Competitive Landscape & Existing Alternatives
| Approach | Primary Mechanism | Critical Weakness | SAT-SA Differentiation |
|---|---|---|---|
| **SOC Maturity Questionnaires (CMM)** | Qualitative self-reported surveys | High risk of bias; entities overstate readiness; cannot verify daily operational discipline | Analyzes actual alert/case execution records rather than self-reported claims |
| **Operational SIEM / SOAR Platforms** | Real-time event correlation & automated alerting | Focuses on active threat mitigation, not supervisory oversight; high alert fatigue; no cross-entity peer benchmarking | Supervisory focus: evaluates the quality, thoroughness, and integrity of how the SOC handled alerts |
| **Traditional KPI Dashboards** | Aggregated metrics (MTTR, MTTD, volume counts) | Highly vulnerable to metric gaming; fast closure times may mask superficial investigation | Tests the operational evidence behind the metrics to distinguish true responsiveness from hurried closure |
| **Manual Spot Sampling** | Examiners inspect 50–100 random cases | Low coverage (1–2%); cannot systematically detect negative space or cross-incident text duplication | Algorithmic triage concentrates expert inspection on cases exhibiting proven anomalous patterns |
| **Generic Anomaly Detection Platforms** | Opaque unsupervised ML scoring | Black-box output ("Anomaly score 0.87") that examiners cannot defend or trace to source records | 100% explainable findings citing deterministic rules, peer percentiles, and exact record citations |

## 3. Core Adoption Barriers & Mitigations
1. **Barrier: Air-Gapped Security Constraints**
   - *Mitigation*: SAT-SA is engineered with zero external network requirements, local SQLite/DuckDB storage, embedded HTML/JS frontend, and self-contained scikit-learn analytics.
2. **Barrier: Fear of "AI Black-Box" Decisions**
   - *Mitigation*: SAT-SA strictly functions as decision support. It generates prioritized *indicators* and *evidence packages*, ensuring the human examiner retains full adjudicative authority.
3. **Barrier: Data Heterogeneity Across CSEs**
   - *Mitigation*: Robust normalization layer that maps diverse SOC schemas into canonical alerts, cases, assets, and escalations while recording data quality issues (`DQ-001` - `DQ-012`).

## 4. Product Positioning Statement
> **For** NCIIPC supervisory examiners and cybersecurity assessment teams,  
> **Who** must assess operational cyber resilience across critical infrastructure entities,  
> **SAT-SA is** an offline, explainable supervisory intelligence platform  
> **That** transforms periodic SOC operational submissions into prioritized manual-review queues, detects hidden execution gaps, and reveals negative space,  
> **Unlike** generic SIEM dashboards or compliance questionnaires that only show high-level metrics or self-reported intentions,  
> **Our product** evaluates actual operational evidence, provides transparent decomposed risk scores, and guarantees 100% auditable record lineage.
