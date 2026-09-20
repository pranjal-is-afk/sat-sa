# 2-Minute Demo Video Recording Guide & Screen Direction
**Problem Statement**: SIH26157 (Supervisory Analytics Tool for SOC Assessment)  
**Target Duration**: 120 seconds  

---

## Screen Direction & Spoken Narration Breakdown

### Sequence 1 (0:00 – 0:15) | The Problem & Context
- **Screen**: Start on `http://127.0.0.1:8000` with the **Portfolio Overview** leaderboard visible.
- **Narration**:  
  > *"NCIIPC assesses the cyber resilience of critical infrastructure entities. While compliance manuals and SLA dashboards show green metrics, operational evidence often hides severe execution breakdowns. SAT-SA is an offline, air-gapped supervisory analytics system that turns periodic operational records into an explainable, prioritized review queue."*

### Sequence 2 (0:15 – 0:35) | Ingestion, Provenance & Quality
- **Screen**: Click to **Submissions & Quality** tab. Show the batch upload interface with SHA-256 hashes and data-quality checks.
- **Narration**:  
  > *"Examiners ingest periodic structured CSV or JSON submissions for alerts, cases, assets, and escalations. SAT-SA immediately computes SHA-256 hashes for data provenance, checks chronological integrity, and quarantines malformed records under rules DQ-001 through DQ-012."*

### Sequence 3 (0:35 – 0:55) | Entity Leaderboard & Decomposed Risk
- **Screen**: Switch to **Portfolio Overview**. Hover over `CSE-04` (score: 82/100) and open its **Entity Deep Dive**.
- **Narration**:  
  > *"Instead of an opaque AI black box, SAT-SA decomposes entity risk into transparent mathematical contributors. Notice CSE-04 flagged with an 82/100 risk score: 31% from unescalated critical alerts, 24% from repeated alerts without remediation, and 18% from unusually fast closures."*

### Sequence 4 (0:55 – 1:15) | Execution Gap Drill-Down
- **Screen**: Click **Prioritized Review Queue**, filter by `CRITICAL`, and click "Drill Down" on Finding `F-INV-002`.
- **Narration**:  
  > *"Drilling down into the evidence, we inspect Finding F-INV-002: a Critical alert closed in just 4 minutes, compared to a sector peer median of 54 minutes. The linked case contains zero investigative steps, zero evidence attachments, and no escalation record."*

### Sequence 5 (1:15 – 1:35) | Negative Space Discovery
- **Screen**: In the Review Queue, select Finding `F-NEG-001` (Negative Space on `AST-SCADA-01`).
- **Narration**:  
  > *"SAT-SA also pioneers negative-space detection: discovering what is missing when it reasonably should exist. Here, a declared Tier-1 SCADA Controller has produced zero telemetry and zero security alerts for 21 consecutive days."*

### Sequence 6 (1:35 – 1:50) | Human Authority & Cryptographic Audit
- **Screen**: Scroll down in the drawer, select Disposition `"Confirmed Execution Gap"`, type *"Verified critical triage breakdown"*, and click **Commit Disposition**. Then switch to **Cryptographic Audit Trail** and click **Verify Cryptographic Chain Integrity**.
- **Narration**:  
  > *"The human supervisor retains final judgement. The examiner records a formal disposition with notes, cryptographically appending the decision to an immutable, SHA-256 chained audit trail."*

### Sequence 7 (1:50 – 2:00) | Supervisory Report & Air-Gap Conclusion
- **Screen**: Switch to **Supervisory Reports**, click **Open Printable HTML Report**, show the formatted executive summary.
- **Narration**:  
  > *"With one click, an evidence-backed assessment report is exported. SAT-SA runs 100% offline, requires zero cloud APIs, and scales expert supervisory oversight across our nation's critical infrastructure."*
