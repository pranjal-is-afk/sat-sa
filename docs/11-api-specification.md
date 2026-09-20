# 11. REST API Specification

## 1. Overview & Base Conventions
- **Base URL**: `/api/v1`
- **Security**: Local Session / Bearer Token (`Authorization: Bearer <token>`)
- **Content Type**: `application/json` (or `multipart/form-data` for file uploads)
- **Error Responses**:
  ```json
  {
    "error_code": "RESOURCE_NOT_FOUND",
    "message": "Entity CSE-99 not found",
    "timestamp": "2026-09-08T11:00:00Z"
  }
  ```

## 2. API Endpoints Catalog

### A. Authentication & Roles
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/login` | Authenticates local user; returns session token & role |
| `GET` | `/auth/me` | Returns current user profile and RBAC permissions |

### B. Submissions & Data Quality
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/submissions/upload` | Ingests CSV/JSON files, computes SHA-256 hash, runs validation |
| `GET` | `/submissions` | Lists all historical submissions and processing status |
| `GET` | `/submissions/{id}/validation` | Retrieves detailed schema and data quality error reports |
| `POST` | `/submissions/{id}/approve` | Promotes validated submission batch to canonical store |

### C. Entities & Supervisory Scores
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/entities` | Returns all CSEs with metadata and sector classification |
| `GET` | `/entities/ranking` | Returns CSEs ranked by supervisory prioritization risk score |
| `GET` | `/entities/{cse_id}` | Returns deep profile of a single CSE with score contributor breakdown |
| `GET` | `/entities/{cse_id}/peer-comparison` | Returns risk-adjusted peer benchmark distributions |

### D. Findings & Review Queue
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/findings` | Returns queryable, filterable findings (by severity, entity, status) |
| `GET` | `/findings/queue` | Returns prioritized human-in-the-loop review queue |
| `GET` | `/findings/{finding_id}` | Returns complete finding details with evidence items and timeline |
| `POST` | `/findings/{finding_id}/disposition` | Records examiner decision (`Confirmed`, `False Positive`, etc.) |

### E. Supervisory Analytics Engine
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analytics-runs` | Triggers supervisory analytics pipeline across entities/periods |
| `GET` | `/analytics-runs/{run_id}` | Retrieves execution stats, rule execution times, and counts |

### F. Reports & Audit
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/reports/generate` | Generates a supervisory assessment report package |
| `GET` | `/reports/{report_id}` | Retrieves generated report content (HTML / printable layout) |
| `GET` | `/audit-events` | Queries append-only audit events and verifies hash chain |
| `GET` | `/audit-events/verify-integrity` | Verifies cryptographic integrity of the entire audit chain |

## 3. Sample Request & Response Payloads

### POST `/api/v1/findings/F-ESC-00021/disposition`
**Request Body**:
```json
{
  "disposition": "Confirmed",
  "reviewer_id": "EXAMINER-07",
  "comment": "Confirmed operational failure: Critical OT gateway alert ALT-8832 was closed with 0 investigation steps and missing mandatory Tier-3 escalation."
}
```

**Response (200 OK)**:
```json
{
  "finding_id": "F-ESC-00021",
  "status": "CONFIRMED",
  "disposition": "Confirmed",
  "reviewed_at": "2026-09-08T11:15:30Z",
  "audit_event_id": "AUD-99182",
  "audit_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```
