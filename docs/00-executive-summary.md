# 00. Executive Summary: SAT-SA

## Problem Statement Context
- **Problem Statement ID**: SIH26157
- **Problem Title**: Supervisory Analytics Tool for SOC Assessment (SAT-SA)
- **Stakeholders / Operational Context**: National Critical Information Infrastructure Protection Centre (NCIIPC) under the National Technical Research Organisation (NTRO).
- **Core Dilemma**: NCIIPC is mandated to assess and enhance the cyber resilience of Critical Sector Entities (CSEs) operating across power grids, banking/financial systems, telecom, transport, defense, and nuclear installations. Today, supervisory examiners rely primarily on manual sampling of periodic SOC data submissions (alerts, incident cases, investigations, escalations, closures). This manual review is indispensable because examiners spot subtle nuances that automated SIEM dashboards conceal; however, manual review cannot scale across hundreds of entities and millions of events.

## One-Line Value Proposition
> **SAT-SA is an offline, air-gapped, explainable supervisory analytics platform that transforms periodic SOC alert and case-management submissions into evidence-backed entity risk indicators and prioritized manual-review queues.**

## What SAT-SA Is — And What It Is NOT
| SAT-SA IS | SAT-SA IS NOT |
|---|---|
| An **offline supervisory analytics tool** for periodic oversight | A real-time SOC or SIEM platform |
| An **evidence-first decision-support platform** for human examiners | An automated incident containment or blocking engine |
| A detector of **execution gaps** (policy claims vs. operational evidence) | A real-time threat hunting or live intrusion detection tool |
| A detector of **negative space** (missing telemetry / silent critical assets) | A continuous log streamer or live packet sniffer |
| A **transparent, decomposed risk scorer** explaining every contributor | An opaque black-box deep learning verdict engine |
| Fully **air-gapped and auditable** with 100% cryptographic data lineage | A cloud-dependent application relying on remote LLMs or APIs |

## Key Capabilities & Differentiators
1. **Execution Gap Detection**: Detects divergence between claimed SOC procedures and operational reality (e.g. Critical alerts closed in <5 minutes with generic boilerplate text, or Critical severity incidents closed without mandatory escalation).
2. **Negative-Space Modeling**: Formulates and uncovers what *should* exist but is missing (e.g. Critical assets declared in inventory with zero alert or telemetry records over a 30-day reporting period).
3. **Transparent Risk Scoring**: Replaces arbitrary risk numbers with a decomposed, weighted attribution formula:
   $$R_{entity} = w_D D + w_I I + w_E E + w_N N + w_P P + w_Q Q$$
   Showing exact percentage contributions (e.g., 31% escalation gaps, 24% repeated alerts).
4. **Prioritized Human-in-the-Loop Review Queue**: Ranks individual cases by severity, evidence completeness, impact, and novelty, putting high-yield supervisory review candidates at the top of the queue.
5. **Auditable Evidence Drill-Down**: Every finding links back to exact raw submitted record IDs, timestamps, rule versions, and peer group baselines.
6. **Air-Gapped Operation**: Engineered to run entirely in an isolated local environment with zero external calls, no external fonts/CDNs, and embedded local storage.

## Target Operational Impact
- **85%+ Reduction in Manual Sampling Time**: Examiners immediately inspect highest-risk anomalies rather than sifting randomly through thousands of benign alerts.
- **Improved Assessment Consistency**: Standardized supervisory rules (`R-ESC-001`, `R-INV-002`, `R-NEG-001`, etc.) apply uniform supervisory scrutiny across all CSEs.
- **Preserved Examiner Authority**: The tool produces indicators and evidence packages; final supervisory disposition (`Confirmed`, `False Positive`, `Needs Escalation`) remains in human hands.
