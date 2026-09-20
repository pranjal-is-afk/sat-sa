# 13. UI/UX Specification Document (UXD)

## 1. Design System & Principles
- **Aesthetic**: Executive Cyber Command Console (Dark Navy `#0A0E17`, Slate `#1E293B`, Electric Cobalt `#2563EB`, Cyber Cyan `#06B6D4`, Alert Amber `#F59E0B`, Critical Crimson `#EF4444`, Success Emerald `#10B981`).
- **Offline First**: Zero external font downloads (system sans-serif stack: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`), embedded local SVGs for icons.
- **Explainability First**: Findings lead with plain-language context before technical metadata; always display supporting record IDs and comparison baselines.
- **Progressive Disclosure**: High-level portfolio leaderboard $\rightarrow$ Entity score contributors $\rightarrow$ Prioritized review queue $\rightarrow$ Finding detail modal $\rightarrow$ Raw record timeline.

## 2. Screen Hierarchy & Navigation
```
[Header: NCIIPC SAT-SA Supervisory Command Console | User: Lead Examiner | Status: Enclave Secure]
├── Navigation Tabs:
│   ├── [1. Portfolio Overview]      (National CSE ranking, macro risk distribution, KPI cards)
│   ├── [2. Entity Deep Dive]        (Decomposed scores, peer radar, asset inventory breakdown)
│   ├── [3. Review Queue]            (Actionable triage queue sorted by P_case, category filters)
│   ├── [4. Submissions & Quality]   (Batch file upload, SHA-256 integrity, DQ quarantine log)
│   ├── [5. Audit & Compliance]      (Append-only chronological log, SHA-256 hash verify)
│   └── [6. Executive Reports]       (One-click printable / exportable supervisory reports)
```

## 3. Detailed Screen Specifications

### Screen 1: Portfolio Overview
- **Top Metrics Row**:
  - `Entities Assessed` (e.g. 10 Active CSEs)
  - `Total Submissions Processed` (e.g. 48,250 records)
  - `Identified Execution Gaps` (e.g. 142 cases flagged)
  - `Negative Space Gaps` (e.g. 18 critical silent assets)
  - `Pending Review Items` (e.g. 34 high-priority items)
- **Ranked Entity Leaderboard Table**:
  - Columns: Rank, Entity ID, Organization Name, Sector, Supervisory Risk Score (0–100 bar), Primary Risk Contributors (badge pills), Action button ("Inspect Entity").

### Screen 2: Entity Deep Dive
- **Entity Header**: Entity Name, Sector (e.g. Power Grid), Tier 1 Infrastructure, Reporting Period.
- **Decomposed Risk Score Breakdown Card**:
  - Displays $R_{entity} = w_D D + w_I I + w_E E + w_N N + w_P P + w_Q Q$.
  - Visual stacked horizontal bar showing percentage contribution:
    - 31% Critical Alert Escalation Gaps
    - 24% Repeated Alerts Without Remediation
    - 18% Fast Closures (<5 mins)
    - 15% Missing Critical Asset Telemetry
    - 12% Incomplete Case Evidence
- **Peer Benchmark Radar & Distribution**:
  - Compares CSE closure median (e.g. 6 min) against Sector Median (54 min) and 5th percentile (12 min).

### Screen 3: Finding Detail & Evidence Drill-Down
- **Finding Header**: Finding ID (`F-ESC-00021`), Category Pill, Severity Badge (`CRITICAL`), Confidence (`96%`).
- **Plain-Language Summary Box**:
  > *"Critical Alert on Critical OT Gateway AST-104 was closed in 4 minutes without an escalation record. The linked case contains 0 investigative workflow steps and 0 attached forensic evidence items. Sector peers escalate 98.4% of similar incidents."*
- **Evidence Comparison Table**:
  | Record Type | Identifier | Evaluated Field | Observed Value | Expected Policy Baseline |
  |---|---|---|---|---|
  | Alert | `ALT-8832` | Severity | `Critical` | Requires mandatory Tier-3 escalation |
  | Asset | `AST-104` | Criticality | `Critical` | Tier-1 Core SCADA Gateway |
  | Case | `CASE-8832` | Duration | `4 mins` | Peer Median: 54 mins |
  | Escalation | `null` | Status | `MISSING` | Mandatory escalation within 60 mins |
- **Chronological Timeline Flow**: Visual flow showing Alert Created $\rightarrow$ Analyst Acknowledged $\rightarrow$ Closed Rapidly $\rightarrow$ (Broken Escalation Link).
- **Human-in-the-Loop Disposition Form**:
  - Decision Dropdown: `Confirmed Execution Gap`, `Needs More Evidence`, `False Positive`, `Remediation Required`.
  - Supervisor Comment Box (Mandatory).
  - "Save Disposition & Append to Audit Trail" Button.
