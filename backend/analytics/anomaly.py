import numpy as np
from typing import Dict
from sklearn.ensemble import IsolationForest

FEATURE_ORDER = [
    'critical_fast_closure_rate', 'escalation_rate', 'mean_closure_time_critical',
    'investigation_text_similarity', 'case_linkage_rate', 'alert_category_coverage',
    'critical_asset_telemetry_ratio', 'low_activity_window_count',
    'closure_time_cv'
]

def run_isolation_forest(all_features: Dict[str, dict]) -> Dict[str, float]:
    """Run IsolationForest. Returns anomaly score (higher = more anomalous, 0-1 range)."""
    cse_ids = list(all_features.keys())
    if len(cse_ids) < 3:
        return {cid: 0.5 for cid in cse_ids}
    
    X = []
    for cid in cse_ids:
        row = [all_features[cid].get(f, 0.0) for f in FEATURE_ORDER]
        X.append(row)
    X = np.array(X, dtype=float)
    
    # Replace NaN with 0
    X = np.nan_to_num(X, nan=0.0)
    
    clf = IsolationForest(contamination=0.1, random_state=42)
    clf.fit(X)
    
    # decision_function returns negative for anomalies; score_samples similar
    raw_scores = clf.decision_function(X)  # higher = more normal
    # Convert: anomaly contribution = -raw_score, then normalize 0-1
    anomaly_raw = -raw_scores
    min_s, max_s = anomaly_raw.min(), anomaly_raw.max()
    if max_s > min_s:
        normalized = (anomaly_raw - min_s) / (max_s - min_s)
    else:
        normalized = np.zeros_like(anomaly_raw)
    
    return {cid: float(normalized[i]) for i, cid in enumerate(cse_ids)}
