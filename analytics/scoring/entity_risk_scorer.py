"""
Entity Supervisory Risk Scorer
Implements transparent decomposed scoring formula:
R_entity = w_D * D + w_I * I + w_E * E + w_N * N + w_P * P + w_Q * Q
No black box: returns exact sub-scores and percentage attribution.
"""

from typing import List, Dict, Any

def calculate_entity_supervisory_risk(
    findings: List[Dict[str, Any]],
    data_quality_issues: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Sub-scores:
    D: Detection & Coverage concerns (0-100)
    I: Investigation quality concerns (0-100)
    E: Escalation breakdown concerns (0-100)
    N: Negative space concerns (0-100)
    P: Peer deviation concerns (0-100)
    Q: Data quality issues (0-100)
    """
    # Initialize component accumulators
    D_count = 0
    I_count = 0
    E_count = 0
    N_count = 0
    P_count = 0

    for f in findings:
        cat = f.get("category", "")
        sev = f.get("severity", "MEDIUM")
        weight = 3.0 if sev == "CRITICAL" else (2.0 if sev == "HIGH" else 1.0)

        if "Escalation" in cat:
            E_count += weight
        elif "Investigation" in cat:
            I_count += weight
        elif "Negative Space" in cat:
            N_count += weight
        elif "Peer Deviation" in cat:
            P_count += weight
        elif "Remediation" in cat or "Detection" in cat:
            D_count += weight

    dq_count = len(data_quality_issues) if data_quality_issues else 0

    # Normalize to 0-100 sub-scores (saturating at 10 high-impact flaws)
    D = min(100.0, D_count * 10.0)
    I = min(100.0, I_count * 8.0)
    E = min(100.0, E_count * 15.0)
    N = min(100.0, N_count * 20.0)
    P = min(100.0, P_count * 12.0)
    Q = min(100.0, dq_count * 5.0)

    # Weights
    w_D = 0.20
    w_I = 0.25
    w_E = 0.25
    w_N = 0.15
    w_P = 0.10
    w_Q = 0.05

    # Composite score
    total_score = round(w_D * D + w_I * I + w_E * E + w_N * N + w_P * P + w_Q * Q, 1)
    
    # Calculate percentage contributions
    raw_sum = (w_D * D) + (w_I * I) + (w_E * E) + (w_N * N) + (w_P * P) + (w_Q * Q)
    contributors = []
    if raw_sum > 0:
        if E > 0:
            contributors.append({"factor": "Critical-Alert Escalation Gaps", "percentage": round((w_E * E / raw_sum) * 100)})
        if D > 0:
            contributors.append({"factor": "Detection & Repeat-Alert Gaps", "percentage": round((w_D * D / raw_sum) * 100)})
        if I > 0:
            contributors.append({"factor": "Fast Closures & Low Evidence", "percentage": round((w_I * I / raw_sum) * 100)})
        if N > 0:
            contributors.append({"factor": "Missing Critical-Asset Telemetry", "percentage": round((w_N * N / raw_sum) * 100)})
        if P > 0:
            contributors.append({"factor": "Peer Metric Deviations", "percentage": round((w_P * P / raw_sum) * 100)})
        if Q > 0:
            contributors.append({"factor": "Data Quality & Schema Defects", "percentage": round((w_Q * Q / raw_sum) * 100)})

    contributors.sort(key=lambda x: x["percentage"], reverse=True)

    tier = "CRITICAL" if total_score >= 75 else ("HIGH" if total_score >= 50 else ("ELEVATED" if total_score >= 25 else "LOW"))

    return {
        "score": total_score,
        "risk_tier": tier,
        "sub_scores": {
            "detection_coverage": round(D, 1),
            "investigation_quality": round(I, 1),
            "escalation_breakdown": round(E, 1),
            "negative_space": round(N, 1),
            "peer_deviation": round(P, 1),
            "data_quality": round(Q, 1)
        },
        "contributors": contributors
    }
