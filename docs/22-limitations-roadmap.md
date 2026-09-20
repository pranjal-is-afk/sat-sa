# 22. Limitations & Strategic Product Roadmap

## 1. System Limitations & Honest Technical Boundaries
A credible supervisory tool must explicitly acknowledge its operational assumptions and boundaries:

1. **Prioritization Signals, Not Unilateral Proof**:
   - An alert closed in 4 minutes or a critical asset producing zero telemetry is a *supervisory risk signal*, not definitive proof of negligence. Operational explanations (e.g. planned maintenance, authorized duplicate deduplication) may exist, which is why human examiner adjudication is mandatory.
2. **Dependence on Submission Completeness**:
   - The quality of negative-space analysis directly depends on the completeness of the declared asset inventory. If an entity omits an asset from its declared inventory, the system cannot detect its silence.
3. **NLP Language Nuances**:
   - TF-IDF similarity flags repetitive investigation notes. However, standardized Standard Operating Procedure (SOP) phrasing (e.g., standard routine antivirus false-positive cleanups) may naturally score high similarity without implying poor investigation.
4. **Offline Environment Boundary**:
   - The platform strictly adheres to air-gapped constraints and does not query external threat intelligence APIs (e.g. VirusTotal or AlienVault OTX) at runtime.

## 2. Multi-Phase Product Roadmap

```mermaid
timeline
    title SAT-SA Evolution Roadmap
    section MVP (Hackathon Delivery)
      Data Upload & Normalization : CSV/JSON, SHA-256 Hashes, DQ-001 to DQ-012
      Core Supervisory Analytics  : 7 Core Rules, Negative Space, TF-IDF NLP
      Triage Console              : Decomposed Scoring, Review Queue, Dispositions
      Air-Gap Proof               : Standalone Local Deployment, Offline Tests
    section Phase 1 (Enclave Pilot)
      Multi-Enclave Replication   : Distributed SQLite/DuckDB Sync
      Granular Sector Taxonomies  : Banking, Telecom, Energy sub-profiles
      Automated PDF Evidence Pack : Formal cryptographic document signing
    section Phase 2 (Advanced Analytics)
      Local Sentence Embeddings   : Vendored offline MiniLM model for semantic clustering
      Automated Shift Profiling   : Shift-level investigation quality analytics
      Rule Studio UI              : Visual rule builder for non-technical examiners
    section Phase 3 (Enterprise Scale)
      High-Availability Cluster   : Active-passive enclave failover
      National Benchmarking Hub   : Anonymized cross-sector federated analytics
```
