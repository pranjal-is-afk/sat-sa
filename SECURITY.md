# Security Policy & Air-Gapped Assurance

## Operational Context
SAT-SA (**Supervisory Analytics Tool for SOC Assessment**) is specifically architected for offline, air-gapped supervisory deployment within an NCIIPC / NTRO controlled enclave. The platform processes sensitive SOC alert and case-management submissions from Critical Sector Entities (CSEs).

## Core Security Commitments
1. **Zero External Network Dependencies**:
   - The application makes no outbound HTTP/S calls, no CDN downloads, no external DNS requests, and relies on no cloud-hosted AI APIs (no OpenAI, Claude, Gemini, or remote inference).
2. **Data at Rest & Integrity Chaining**:
   - All raw uploads are SHA-256 hashed immediately upon intake and preserved immutably.
   - Audit trail records are cryptographically linked using SHA-256 state chaining.
3. **Defense-in-Depth Against Ingestion Attacks**:
   - **CSV Formula Injection Prevention**: Leading characters (`=`, `+`, `-`, `@`, `\t`, `\r`) are sanitized or escaped prior to display and export.
   - **Strict Input Validation**: Pydantic schema validation and format limits prevent memory exhaustion or parser disruption.
   - **SQL Injection Prevention**: 100% parameterized queries across all database operations.
   - **XSS Mitigation**: Context-aware HTML escaping for all case investigation notes, step descriptions, and user inputs.
4. **Role-Based Access Control (RBAC)**:
   - Built-in roles enforce principle of least privilege:
     - `Supervisory Examiner`: Can view entities, findings, drill into evidence, and record dispositions.
     - `Lead Supervisor`: Can approve assessments, adjust priority thresholds, and export official reports.
     - `Data Administrator`: Can upload submissions, inspect validation errors, and manage CSE mappings.
     - `System Administrator`: Operates database maintenance, backups, and user management.
     - `Auditor`: Read-only access to immutable audit events, source file hashes, and rule versions.

## Reporting a Vulnerability
Security issues should be reported to the local administrative security officer or logged into the local enclave defect management registry. In accordance with air-gap protocols, do not transmit internal traces or entity data outside the security perimeter.
