"""
Unit Tests for Entity Supervisory Risk Scoring & Prioritization
"""

from analytics.scoring.entity_risk_scorer import calculate_entity_supervisory_risk
from analytics.scoring.case_prioritizer import prioritize_findings

def test_entity_risk_scoring_healthy():
    findings = [] # No flaws
    result = calculate_entity_supervisory_risk(findings)
    assert result["score"] == 0.0
    assert result["risk_tier"] == "LOW"
    assert len(result["contributors"]) == 0

def test_entity_risk_scoring_decomposed_weights():
    findings = [
        {"category": "Escalation Weakness", "severity": "HIGH"},
        {"category": "Escalation Weakness", "severity": "HIGH"},
        {"category": "Investigation Weakness", "severity": "HIGH"},
        {"category": "Negative Space", "severity": "HIGH"},
    ]
    result = calculate_entity_supervisory_risk(findings)
    assert result["score"] > 0.0
    assert "contributors" in result
    assert len(result["contributors"]) > 0
    # Confirm percentage attribution exists and sums close to 100%
    total_pct = sum(c["percentage"] for c in result["contributors"])
    assert 95 <= total_pct <= 105

def test_case_prioritizer_ranking():
    findings = [
        {"finding_id": "F-LOW", "severity": "LOW", "category": "Operational Discipline", "confidence": 0.8},
        {"finding_id": "F-CRIT", "severity": "CRITICAL", "category": "Escalation Weakness", "confidence": 0.95},
        {"finding_id": "F-MED", "severity": "MEDIUM", "category": "Investigation Weakness", "confidence": 0.85}
    ]
    ranked = prioritize_findings(findings)
    assert ranked[0]["finding_id"] == "F-CRIT"
    assert ranked[-1]["finding_id"] == "F-LOW"
    assert ranked[0]["priority_score"] > ranked[1]["priority_score"]
