# 21. Demo Script & Evaluation Narrative (2-Minute Walkthrough)

## Evaluation Narrative Overview
- **Core Message**: *"SAT-SA transforms massive, periodic SOC operational records into a clear, explainable, and prioritized manual-review queue, surfacing hidden execution gaps and negative space that traditional dashboards miss."*
- **Duration**: Exactly 2 minutes (120 seconds).
- **Target Audience**: SIH Technical Evaluators & NCIIPC Jury Members.

---

## 2-Minute Step-by-Step Script

| Timestamp | UI Screen / Action | Spoken Narration Script | Key Technical Point Highlighted |
|---|---|---|---|
| **0:00 – 0:15** | **Main Dashboard**<br>Display top KPI cards & National Leaderboard | *"NCIIPC oversees critical infrastructure cybersecurity. But compliance reports and SLA dashboards often hide critical weaknesses. SAT-SA is an offline, air-gapped supervisory analytics system that turns periodic operational evidence into prioritized review queues."* | Not a SIEM; supervisory analytics for NCIIPC; air-gap compliance. |
| **0:15 – 0:35** | **Submission Manager**<br>Demonstrate CSV batch ingestion & SHA-256 integrity | *"Examiners upload periodic submissions for alerts, cases, assets, and escalations. Before processing, SAT-SA validates schemas, checks chronological integrity, logs quarantined rows, and computes SHA-256 hashes to guarantee data provenance."* | Ingestion robustness; DQ-001 to DQ-012; data lineage. |
| **0:35 – 0:55** | **Entity Ranking View**<br>Show CSE-04 at top with decomposed risk score | *"Rather than an opaque black box, SAT-SA ranks entities by transparent supervisory risk. Notice CSE-04 flagged with an 82/100 risk score: 31% from unescalated critical alerts, 24% from repeated alerts without remediation, and 18% from unusually fast closures."* | Transparent score decomposition: $R = \sum w_i S_i$; no black box. |
| **0:55 – 1:15** | **Execution Gap Drill-Down**<br>Click Finding `F-INV-002` (Fast Closure) | *"Drilling into CSE-04, we open Finding F-INV-002: a Critical alert closed in just 4 minutes, compared to a sector median of 54 minutes. The linked incident case has 0 investigation steps, 0 evidence files, and no escalation record."* | Finding explainability; plain-language reason; exact record citations. |
| **1:15 – 1:35** | **Negative-Space Discovery**<br>Click Finding `F-NEG-001` (Missing Telemetry) | *"SAT-SA also pioneers negative-space detection: discovering what is missing when it reasonably should exist. Here, Asset AST-104—a declared Tier-1 SCADA Controller—has produced zero telemetry or alerts for 21 consecutive days."* | Negative space ($C_{asset} = 0$); reveals blindspots that normal SIEMs miss. |
| **1:35 – 1:50** | **Human-in-the-Loop Review**<br>Examiner records formal disposition & comment | *"The supervisor retains complete control. The examiner reviews the evidence timeline, marks the finding as 'Confirmed Execution Gap', inputs supervisory comments, and cryptographically commits the action to the append-only audit trail."* | Human authority preserved; tamper-evident SHA-256 audit chaining. |
| **1:50 – 2:00** | **Report Export & Conclusion**<br>Generate Executive PDF/HTML Evidence Pack | *"With one click, an evidence-backed assessment report is exported. SAT-SA runs 100% offline, requires zero cloud APIs, and scales expert supervisory review across our nation's critical infrastructure."* | One-click reporting; air-gapped readiness; strong conclusion. |
