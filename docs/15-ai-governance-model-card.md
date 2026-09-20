# 15. AI / ML Governance & Model Card Document

## 1. Executive Analytics Positioning
> **SAT-SA does not depend on generative AI, cloud LLM APIs, or opaque black-box neural networks.**  
> Its analytics architecture is intentionally hybrid: combining **deterministic supervisory rules**, **robust non-parametric statistics**, **offline TF-IDF text similarity**, and an **unsupervised Isolation Forest**. This design guarantees 100% offline air-gapped deployment, complete mathematical explainability, and defensible auditability before national authorities.

## 2. Model Card: Local TF-IDF Cosine Similarity (`NLP-SIM-01`)

### A. Model Overview
- **Model Name**: TF-IDF Investigation Narrative Vectorizer
- **Version**: 1.1.0
- **Purpose**: Detect copy-pasted, templated, or superficial investigation summaries across disparate cases.
- **Library**: `scikit-learn.feature_extraction.text.TfidfVectorizer`
- **Deployment**: 100% local, CPU-bound, zero network requirements.

### B. Parameters & Configuration
- `max_features`: 10,000
- `ngram_range`: (1, 3) (Unigrams, bigrams, trigrams)
- `stop_words`: 'english' (standard pre-packaged local stopword list)
- `min_df`: 2 (terms must appear in at least 2 documents)
- `sublinear_tf`: True (dampens effect of repetitive words)
- `Similarity Threshold`: 0.85 (cosine similarity $\ge 0.85$ triggers supervisory candidate flag)

### C. Explainability & Human Oversight
- When similarity is flagged, the system outputs:
  1. The exact pairwise similarity score (e.g. 93.4%).
  2. The shared overlapping n-gram tokens (e.g. *"system logs verified no malicious persistence observed host restored to baseline"*).
  3. The differing attributes (e.g. Alert Category A vs Category B, Asset X vs Asset Y).
- Human examiners review whether identical phrasing represents legitimate standard operating procedure (e.g., standard ping timeout) or superficial investigation.

---

## 3. Model Card: Isolation Forest Multidimensional Outlier Detector (`ML-ISO-01`)

### A. Model Overview
- **Model Name**: Multivariate SOC Operational Isolation Forest
- **Version**: 1.0.0
- **Purpose**: Detect anomalous multidimensional combinations of behavior across reporting periods (e.g. sudden drop in alert rate combined with rapid closure time and zero escalations).
- **Library**: `scikit-learn.ensemble.IsolationForest`

### B. Input Features
1. Normalized alert rate per asset-day.
2. Median alert closure duration ($T_{closure}$).
3. Escalation ratio for Critical/High alerts.
4. Investigation evidence density (average attachments/steps per case).
5. Repeat alert ratio ($R_{repeat}$).
6. Negative space asset ratio (silent critical assets / total critical assets).

### C. Governance & Safety Guardrails
- **No Autonomous Penalty**: Isolation Forest outputs an "Anomalous Operational Profile" signal; it never unilaterally penalizes or reduces an entity's compliance status.
- **Deterministic Precedence**: Deterministic rule failures (`R-ESC-001`) always take precedence over ML scores.
- **Model Update Governance**: Models are retrained or re-calibrated offline only through signed configuration packages evaluated against a frozen benchmark test set.
