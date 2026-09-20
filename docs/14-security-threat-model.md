# 14. Security Specification & Threat Model

## 1. Security Context & Objectives
SAT-SA processes sensitive operational telemetry and incident narratives from national Critical Sector Entities (CSEs). The system is deployed within an air-gapped NCIIPC enclave. Security must be an architectural foundation, not an afterthought.

Core Objectives:
- Guarantee zero network leakage or unauthorized telemetry egress.
- Protect data confidentiality and prevent unauthorized cross-entity data exposure.
- Enforce cryptographic integrity and data provenance over all submitted evidence.
- Maintain tamper-evident, append-only audit records for all human supervisory decisions.

## 2. Threat Modeling Matrix (STRIDE Analysis)

| Threat Category | Specific Threat Scenario | Impact | Built-in Mitigation in SAT-SA |
|---|---|---|---|
| **Spoofing** | Malicious insider attempts to impersonate Lead Examiner to dismiss critical findings | Unauthorized finding dismissal | Local session-based RBAC; role enforcement at router level; mandatory audit logging |
| **Tampering** | User alters raw submission records or edits historic findings to conceal SOC failure | Evidence falsification | Raw file SHA-256 calculation at ingestion; SQLite append-only audit log with cryptographic hash chaining |
| **Repudiation** | Examiner denies marking an entity finding as "False Positive" | Lack of accountability | Audit trail logs immutable user ID, timestamp, prior state, new state, and SHA-256 hash |
| **Information Disclosure** | Unauthorized export of cross-entity intelligence to unauthorized personnel | Sensitive infrastructure data leak | Role-based export gating; local file watermarking; zero external internet pathways |
| **Denial of Service** | "Zip bomb" or massive malformed CSV crafted to exhaust server memory during parsing | Processing disruption | Strict file size limits (50MB); chunked streaming parsers; quarantine isolation |
| **Elevation of Privilege** | Data Administrator gains access to override analytics rules or examiner dispositions | Unauthorized policy tampering | Strict role separation (`Data Admin` vs `Supervisory Examiner` vs `Lead Supervisor`) |

## 3. Defense Against Ingestion Attacks

### A. CSV Formula Injection Defense
Attackers may inject spreadsheet formula payloads (e.g. `=cmd|' /C calc'!A0` or `@SUM(...)`) into case investigation summaries to execute code when examiners export CSVs.  
**Mitigation**: The normalization and export services automatically prefix sensitive characters (`=`, `+`, `-`, `@`, `\t`, `\r`) with a single apostrophe `'` and enforce strict HTML escaping before rendering.

### B. SQL Injection Prevention
Direct SQL string concatenation is strictly prohibited. 100% of SQLite database queries use parameterized parameter bindings:
```python
# CORRECT & ENFORCED:
cursor.execute("SELECT * FROM alert WHERE cse_id = ? AND severity = ?", (cse_id, severity))
```

### C. Cross-Site Scripting (XSS) Prevention
Case notes and analyst summaries may contain raw HTML or script tags. All user-supplied strings are escaped via standard HTML entity encoding prior to template rendering or frontend injection.

## 4. Air-Gapped Network Verification Checklist
- [x] Socket binds strictly to `127.0.0.1` or authorized enclave subnet.
- [x] Zero outbound HTTP/HTTPS requests in application code.
- [x] Zero external font, stylesheet, or JavaScript CDN `<link>` or `<script>` tags.
- [x] Local storage for all models, dependencies, schemas, and assets.
