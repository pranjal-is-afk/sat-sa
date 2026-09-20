"""
Local Unsupervised Isolation Forest Anomaly Detector
Fits a local multivariate Isolation Forest across entity operational feature vectors
to discover novel multi-dimensional operational anomalies.
"""

from typing import List, Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest

def run_multivariate_anomaly_detection(
    entity_metrics: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Takes entity feature vectors:
    [alert_rate, median_closure_mins, escalation_rate, evidence_density, repeat_ratio, negative_space_ratio]
    and computes anomaly score (-1 for outlier, 1 for inlier).
    """
    if len(entity_metrics) < 4:
        return [] # Require sufficient population for baseline

    feature_matrix = []
    cse_ids = []

    for em in entity_metrics:
        features = [
            em.get("alert_rate", 0.0),
            em.get("median_closure_mins", 50.0),
            em.get("escalation_rate", 0.5),
            em.get("evidence_density", 2.0),
            em.get("repeat_ratio", 0.1),
            em.get("negative_space_ratio", 0.0)
        ]
        feature_matrix.append(features)
        cse_ids.append(em.get("cse_id"))

    X = np.array(feature_matrix)
    
    # Train local Isolation Forest
    iso = IsolationForest(contamination=0.25, random_state=42)
    predictions = iso.fit_predict(X)
    raw_scores = iso.decision_function(X) # lower score = more abnormal

    anomaly_findings = []
    for idx, pred in enumerate(predictions):
        if pred == -1: # Outlier detected
            cid = cse_ids[idx]
            anomaly_score = float(-raw_scores[idx])
            anomaly_findings.append({
                "finding_id": f"F-ML-ISO-{cid}",
                "entity_id": cid,
                "rule_id": "ML-ISO-01",
                "rule_version": "1.0.0",
                "category": "Peer Deviation",
                "type": "MULTIVARIATE_OPERATIONAL_ANOMALY",
                "severity": "MEDIUM",
                "confidence": min(0.90, 0.65 + anomaly_score),
                "status": "OPEN",
                "case_id": None,
                "alert_id": None,
                "asset_id": None,
                "reason": f"Multivariate Isolation Forest flagged entity {cid} as exhibiting an anomalous combination of operational behaviors (anomaly score: {anomaly_score:.2f}).",
                "evidence": [
                    {"table": "entities", "record_id": cid, "field": "multivariate_anomaly_score", "value": round(anomaly_score, 3)},
                    {"table": "entities", "record_id": cid, "field": "feature_vector", "value": feature_matrix[idx]}
                ],
                "peer_baseline": "Entity vector deviates from baseline multi-dimensional cluster center.",
                "recommended_action": "Review multi-dimensional operations profile to check for atypical operational model."
            })

    return anomaly_findings
