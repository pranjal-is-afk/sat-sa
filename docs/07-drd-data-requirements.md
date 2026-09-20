# 07. Data Requirements Document (DRD)

## 1. Data Scope & Ingestion Format
SAT-SA ingests periodic structured submissions representing SOC operations. To ensure operational feasibility and preserve operational security, the system does not process full packet captures, raw payloads, or customer confidential records. It operates purely on **structured operational and case-management metadata**.

Supported ingestion formats:
- **CSV** (Comma-Separated Values, RFC 4180 compliant)
- **JSON** (JSON array or NDJSON)

## 2. Canonical Data Entities & Schemas

### A. Alert Table (`alerts`)
| Field | Type | Mandatory | Description |
|---|---|---|---|
| `alert_id` | String | Yes | Unique alert identifier (e.g. `ALT-10023`) |
| `cse_id` | String | Yes | Submitting entity identifier (e.g. `CSE-04`) |
| `created_at` | Timestamp (ISO-8601) | Yes | Time alert was triggered by detection source |
| `acknowledged_at` | Timestamp (ISO-8601) | No | Time analyst opened/acknowledged alert |
| `closed_at` | Timestamp (ISO-8601) | No | Time alert was resolved/dispositioned |
| `severity` | Enum (`Critical`,`High`,`Medium`,`Low`) | Yes | Assigned threat severity |
| `alert_category` | String | Yes | Classification (e.g. `Malware`, `Identity`, `Lateral Movement`) |
| `source_system` | String | No | Detection source (e.g. `EDR`, `NDR`, `Firewall`, `IAM`) |
| `asset_id` | String | No | Target asset key (e.g. `AST-104`) |
| `asset_criticality` | Enum (`Critical`,`High`,`Medium`,`Low`) | No | Asset tier |
| `status` | Enum (`Open`,`Acknowledged`,`Investigated`,`Closed`,`Escalated`) | Yes | Operational alert state |
| `disposition` | String | No | Resolution tag (e.g. `True Positive`, `False Positive`, `Benign`) |
| `case_id` | String | No | Linked investigation case identifier |
| `escalation_id` | String | No | Linked escalation record |
| `analyst_id` | String | No | Pseudonymized analyst ID (e.g. `ANON-042`) |
| `business_service` | String | No | Impacted business service (e.g. `SCADA Gateway`) |

### B. Case Table (`cases`)
| Field | Type | Mandatory | Description |
|---|---|---|---|
| `case_id` | String | Yes | Unique case identifier (e.g. `CASE-8832`) |
| `cse_id` | String | Yes | Entity identifier |
| `alert_id` | String | No | Primary originating alert |
| `created_at` | Timestamp (ISO-8601) | Yes | Case creation time |
| `investigation_started_at` | Timestamp (ISO-8601) | No | Investigation initiation timestamp |
| `closed_at` | Timestamp (ISO-8601) | No | Case closure timestamp |
| `priority` | Enum (`Critical`,`High`,`Medium`,`Low`) | No | Case response priority |
| `investigation_summary` | Text | No | Narrative notes written by analyst |
| `evidence_count` | Integer | No | Count of forensic artifacts/logs attached |
| `closure_reason` | String | No | Detailed closure justification |
| `root_cause` | String | No | Root cause analysis findings |
| `remediation_status` | String | No | Status of corrective action plan |
| `reviewer_id` | String | No | Pseudonymized lead reviewer |

### C. Investigation Workflow Steps (`investigation_steps`)
| Field | Type | Mandatory | Description |
|---|---|---|---|
| `step_id` | String | Yes | Step record ID |
| `case_id` | String | Yes | Parent case reference |
| `step_name` | String | Yes | Triage action (e.g. `Memory Dump`, `Host Isolation`) |
| `step_status` | Enum (`Pending`,`Completed`,`Failed`) | Yes | Execution status |
| `performed_by` | String | No | Pseudonymized analyst |
| `started_at` | Timestamp | No | Step start time |
| `completed_at` | Timestamp | No | Step finish time |
| `notes` | Text | No | Step specific analyst notes |
| `evidence_reference`| String | No | Hash or pointer to artifact |

### D. Escalations (`escalations`)
| Field | Type | Mandatory | Description |
|---|---|---|---|
| `escalation_id` | String | Yes | Escalation identifier |
| `case_id` | String | Yes | Linked case identifier |
| `escalation_level` | String | Yes | Tier (e.g. `Tier 3`, `Incident Commander`, `CERT`) |
| `escalated_to` | String | Yes | Receiving entity / body |
| `escalated_at` | Timestamp | Yes | Escalation dispatch time |
| `reason` | Text | Yes | Escalation rationale |
| `acknowledged_at` | Timestamp | No | External acknowledgement time |
| `status` | String | Yes | Status (e.g. `Dispatched`, `Acknowledged`, `Resolved`) |

### E. Assets (`assets`)
| Field | Type | Mandatory | Description |
|---|---|---|---|
| `asset_id` | String | Yes | Unique asset code |
| `cse_id` | String | Yes | Entity identifier |
| `asset_type` | String | Yes | Device type (e.g. `OT Controller`, `Active Directory`, `Database`) |
| `business_service` | String | Yes | Associated function |
| `criticality` | Enum (`Critical`,`High`,`Medium`,`Low`) | Yes | Impact tier |
| `environment` | String | No | Environment (e.g. `Production`, `SCADA DMZ`, `Corporate`) |
| `monitoring_expected`| Boolean | Yes | Flag indicating whether telemetry is expected |
| `monitoring_source` | String | No | Designated collector tool |

### F. Telemetry Coverage (`telemetry_coverage`)
| Field | Type | Mandatory | Description |
|---|---|---|---|
| `asset_id` | String | Yes | Target asset key |
| `period` | String | Yes | Time period (e.g. `2026-08`) |
| `expected_event_volume`| Integer | Yes | Projected baseline volume |
| `observed_event_volume`| Integer | Yes | Actual ingested volume |
| `last_seen_at` | Timestamp | No | Latest recorded heartbeat |
| `coverage_status` | Enum (`Active`,`Intermittent`,`Silent`) | Yes | Operational state |

### G. Remediations (`remediations`)
| Field | Type | Mandatory | Description |
|---|---|---|---|
| `remediation_id` | String | Yes | Remediation tracking code |
| `asset_id` | String | Yes | Asset requiring remediation |
| `case_id` | String | No | Originating incident case |
| `vulnerability_or_root_cause`| String | Yes | Root vulnerability or weakness |
| `action_plan` | Text | Yes | Mitigation plan |
| `status` | Enum (`Planned`,`In_Progress`,`Completed`,`Overdue`) | Yes | Execution state |
| `due_date` | Date | No | Remediation deadline |

## 3. Data-Quality Rules (DQ-001 through DQ-012)
- **DQ-001**: Every submission record must contain a valid, non-null `cse_id`.
- **DQ-002**: `alert_id` must be globally unique per CSE reporting period.
- **DQ-003**: `closed_at` must not be chronologically earlier than `created_at`.
- **DQ-004**: `acknowledged_at` must not be chronologically earlier than `created_at`.
- **DQ-005**: If `case_id` is populated in alerts, it must resolve to an existing record in `cases`.
- **DQ-006**: If `escalation_id` is populated in cases, it must resolve to an existing record in `escalations`.
- **DQ-007**: Severities must strictly conform to allowed enum values (`Critical`, `High`, `Medium`, `Low`).
- **DQ-008**: Alert `asset_id` values must resolve to valid assets in the CSE's asset inventory.
- **DQ-009**: Duplicate submission records are flagged and quarantined.
- **DQ-010**: Records with unparseable timestamps or missing primary keys are routed to the quarantine log.
- **DQ-011**: Raw submission SHA-256 hashes must be calculated and stored before parsing.
- **DQ-012**: Submission data completeness metrics are generated per file and entity.
