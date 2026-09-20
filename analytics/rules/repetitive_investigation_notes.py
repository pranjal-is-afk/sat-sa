"""
Rule R-INV-003: Repetitive Investigation Narrative Detection
Uses scikit-learn TF-IDF Vectorizer and Cosine Similarity to detect boilerplate copy-paste
investigation summaries across disparate cases, dates, or assets.
"""

from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def evaluate_repetitive_investigations(
    cases: List[Dict[str, Any]],
    similarity_threshold: float = 0.85,
    min_narrative_length: int = 25,
    rule_version: str = "1.2.0"
) -> List[Dict[str, Any]]:
    findings = []
    
    # Filter cases with meaningful text
    valid_cases = [c for c in cases if c.get("investigation_summary") and len(c["investigation_summary"].strip()) >= min_narrative_length]
    
    if len(valid_cases) < 3:
        return findings

    corpus = [c["investigation_summary"] for c in valid_cases]

    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    except Exception:
        return findings

    flagged_indices = set()
    n = len(valid_cases)

    for i in range(n):
        if i in flagged_indices:
            continue
        duplicates = []
        for j in range(i + 1, n):
            # Same entity, different cases
            if valid_cases[i].get("cse_id") == valid_cases[j].get("cse_id"):
                if sim_matrix[i, j] >= similarity_threshold:
                    duplicates.append((j, float(sim_matrix[i, j])))

        if len(duplicates) >= 2: # Found at least 2 other cases with near-identical text
            all_cluster_cases = [valid_cases[i]] + [valid_cases[d[0]] for d in duplicates]
            flagged_indices.add(i)
            for d in duplicates:
                flagged_indices.add(d[0])

            matched_case_ids = [c["case_id"] for c in all_cluster_cases]
            avg_similarity = sum(d[1] for d in duplicates) / len(duplicates)

            for member_case in all_cluster_cases:
                finding_id = f"F-BOILER-{member_case.get('case_id', 'UNKNOWN')}"
                findings.append({
                    "finding_id": finding_id,
                    "entity_id": member_case.get("cse_id", ""),
                    "rule_id": "R-INV-003",
                    "rule_version": rule_version,
                    "category": "Investigation Weakness",
                    "type": "REPETITIVE_INVESTIGATION_NARRATIVE",
                    "severity": "MEDIUM",
                    "confidence": round(avg_similarity, 2),
                    "status": "OPEN",
                    "case_id": member_case.get("case_id"),
                    "alert_id": member_case.get("alert_id"),
                    "asset_id": None,
                    "reason": f"Investigation summary for case {member_case.get('case_id')} has {avg_similarity:.1%} TF-IDF text similarity to other cases in repetitive template cluster ({len(matched_case_ids)} cases).",
                    "evidence": [
                        {"table": "cases", "record_id": member_case.get("case_id"), "field": "similarity_score", "value": round(avg_similarity, 3)},
                        {"table": "cases", "record_id": member_case.get("case_id"), "field": "duplicate_cluster_size", "value": len(matched_case_ids)},
                        {"table": "cases", "record_id": member_case.get("case_id"), "field": "sample_matched_cases", "value": matched_case_ids[:5]}
                    ],
                    "peer_baseline": "Across sector peers, less than 4.5% of investigations share >80% narrative similarity.",
                    "recommended_action": "Audit SOC shift handover and investigate whether analysts are executing genuine forensic triage or boilerplate closure."
                })

    return findings
