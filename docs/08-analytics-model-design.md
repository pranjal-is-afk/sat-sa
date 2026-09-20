# 08. Analytics & Model Design Document (AMD)

## 1. Analytics Guiding Principles
1. **Explainability Over Black-Box Complexity**: Every finding must state *what* was detected, *why* it was flagged, *which* baseline or threshold was used, and cite the *exact record IDs*.
2. **Operational Evidence Over Stated Compliance**: Metrics test whether operations worked in practice rather than whether policies look sound on paper.
3. **Negative-Space as a First-Class Citizen**: Absence of expected security evidence is evaluated as rigorously as presence of abnormal activity.
4. **Human-in-the-Loop Adjudication**: Algorithms output *prioritized review candidates*, not unilateral verdicts of misconduct.

## 2. Supervisory Signal Taxonomy
```
┌──────────────────────────────────────────────────────────┐
│              Supervisory Analytics Signals               │
├─────────────────────────┬────────────────────────────────┤
│ 1. Execution Gaps       │ 2. Negative Space              │
│ - Fast closure          │ - Silent critical assets       │
│ - Missing escalation    │ - Missing expected categories  │
│ - Boilerplate notes     │ - Broken workflow links        │
├─────────────────────────┼────────────────────────────────┤
│ 3. Peer Deviations      │ 4. Operational Discipline      │
│ - Percentile outliers   │ - Inverted timestamps          │
│ - Volume anomalies      │ - Pre-investigation closures   │
│ - Rate deviations       │ - Metric / SLA gaming          │
└─────────────────────────┴────────────────────────────────┘
```

## 3. Mathematical Formulations & Rule Definitions

### A. High-Severity Fast Closure (`R-INV-002`)
Calculates closure duration:
$$T_{closure} = T_{closed} - T_{created}$$

A case is flagged if:
- $\text{Severity} \in \{\text{'Critical'}, \text{'High'}\}$
- $T_{closure} < \Theta_{fast}$ (e.g. 10 minutes) OR $T_{closure} < P_{05}(\text{Peer Group})$
- $\text{Evidence Count} \le 1$ OR $\text{Escalation Record} = \text{null}$

### B. Investigation Quality Scoring (`R-INV-001`)
Evaluates the depth and substantive effort behind case resolution:
$$Q_{investigation} = w_1 E + w_2 W + w_3 R + w_4 A + w_5 D$$
Where:
- $E \in [0, 1]$: Forensic evidence completeness ($\min(1.0, \text{count} / 3)$)
- $W \in [0, 1]$: Investigation workflow step completion
- $R \in [0, 1]$: Root cause documentation presence and specificity
- $A \in [0, 1]$: Analyst reasoning length ($> 50$ characters non-boilerplate)
- $D \in [0, 1]$: Differentiation from common template boilerplate

Weights: $w_1 = 0.25, w_2 = 0.25, w_3 = 0.20, w_4 = 0.15, w_5 = 0.15$.  
Flagged when $Q_{investigation} < 0.40$ on high-priority incidents.

### C. Repetitive Investigation Pattern Detection (`R-INV-003`)
Detects copy-pasted or templated investigation notes across unrelated cases using **TF-IDF vectorization and Cosine Similarity**:
$$\text{Similarity}(d_i, d_j) = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\| \|\mathbf{v}_j\|}$$
Cases $d_i, d_j$ are flagged when:
- $\text{Similarity}(d_i, d_j) \ge 0.85$
- Assets, dates, or alert categories differ
- Rationale: High similarity indicates template-driven, superficial sign-offs without genuine investigation.

### D. Critical Alert Missing Escalation (`R-ESC-001`)
Deterministic cross-table evaluation against escalation policy matrix:
| Severity | Asset Criticality | Mandatory Escalation |
|---|---|---|
| Critical | Critical | **Mandatory** |
| High | Critical | **Mandatory** |
| High | Medium | Conditional |
| Low | Any | Optional |

Flagged if:
- $\text{Alert Severity} = \text{'Critical'} \land \text{Asset Criticality} = \text{'Critical'}$
- No record exists in `escalations` referencing `alert.case_id` within the mandatory SLA window.

### E. Repeated Alerts Without Remediation (`R-REM-001`)
Evaluates recurring operational failures:
$$R_{repeat} = \frac{\text{Repeated Alerts on Asset After First Occurrence}}{\text{Total Alerts on Asset}}$$
Flagged if:
- $R_{repeat} \ge 0.60$ and alert count $\ge 5$ in 30 days
- No linked record in `remediations` with status $\in \{\text{'In\_Progress'}, \text{'Completed'}\}$

### F. Negative Space: Silent Critical Asset Detection (`R-NEG-001`)
For every critical asset in declared inventory:
$$C_{asset} = \begin{cases} 1 & \text{if expected telemetry or alert evidence exists in reporting period} \\ 0 & \text{otherwise} \end{cases}$$
Flagged if:
- $\text{Asset Criticality} = \text{'Critical'} \land \text{monitoring\_expected} = \text{true}$
- $C_{asset} = 0$ for duration $\ge 14$ consecutive days

### G. Normalized Alert Rate Benchmarking (`R-BEN-001`)
Controls for size disparity between entities:
$$\text{Alert Rate} = \frac{\text{Total Alerts in Period}}{\text{Monitored Assets} \times \text{Reporting Days}}$$
Uses robust non-parametric statistics (Median, Interquartile Range, Median Absolute Deviation) to flag entities falling below the 5th percentile or exceeding the 95th percentile among sector peers.

### H. Decomposed Entity Supervisory Risk Score
$$R_{entity} = w_D D + w_I I + w_E E + w_N N + w_P P + w_Q Q$$
Where:
- $D$: Detection & coverage concerns (score 0–100)
- $I$: Investigation-quality concerns (score 0–100)
- $E$: Escalation breakdown concerns (score 0–100)
- $N$: Negative-space indicators (score 0–100)
- $P$: Peer-deviation indicators (score 0–100)
- $Q$: Data-quality concerns (score 0–100)
Weights: $w_D = 0.20, w_I = 0.25, w_E = 0.25, w_N = 0.15, w_P = 0.10, w_Q = 0.05$.

The system presents the exact contributor breakdown in the UI:
```
CSE-04: High Supervisory Attention — 78/100
Main Contributors:
- 31%: Critical-alert escalation gaps
- 24%: Repeated alerts without remediation
- 18%: Unusually fast closures
- 15%: Missing critical-asset coverage
- 12%: Incomplete investigation evidence
```

### I. Review Queue Prioritization Score
$$P_{case} = \text{Severity} \times \text{Evidence Strength} \times \text{Potential Impact} \times \text{Novelty}$$
Ensures examiners review the most critical, anomalous, and impactful evidence items first.

## 4. Structured Finding Object Format
Every finding emitted by the engine conforms to this canonical structure:
```json
{
  "finding_id": "F-ESC-00021",
  "entity_id": "CSE-04",
  "rule_id": "R-ESC-001",
  "rule_version": "1.2.0",
  "category": "Escalation Weakness",
  "type": "Critical Alert Missing Escalation",
  "severity": "HIGH",
  "confidence": 0.95,
  "status": "OPEN",
  "created_at": "2026-09-08T10:30:00Z",
  "case_id": "CASE-8832",
  "alert_id": "ALT-8832",
  "asset_id": "AST-104",
  "reason": "Critical alert on critical asset AST-104 was closed without an escalation record.",
  "evidence": [
    {"table": "alerts", "record_id": "ALT-8832", "field": "severity", "value": "Critical"},
    {"table": "assets", "record_id": "AST-104", "field": "criticality", "value": "Critical"},
    {"table": "escalations", "record_id": null, "field": "escalation_id", "value": "MISSING"}
  ],
  "peer_baseline": "Sector peer escalation rate for Critical alerts is 98.4%",
  "recommended_action": "Request escalation logs and interview shift lead regarding ALT-8832 disposition.",
  "supervisor_disposition": null
}
```
