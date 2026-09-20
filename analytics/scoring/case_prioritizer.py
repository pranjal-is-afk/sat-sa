"""
Case & Finding Prioritizer
Ranks findings into a manual-review queue using priority formula:
P_finding = Severity_weight * Evidence_weight * Impact_weight * Novelty_weight
Ensures highest-yield supervisory candidates are presented first.
"""

from typing import List, Dict, Any

def prioritize_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    prioritized = []

    sev_map = {"CRITICAL": 4.0, "HIGH": 3.0, "MEDIUM": 2.0, "LOW": 1.0}
    cat_impact_map = {
        "Escalation Weakness": 1.5,
        "Negative Space": 1.4,
        "Remediation Weakness": 1.3,
        "Investigation Weakness": 1.2,
        "Peer Deviation": 1.1,
        "Operational Discipline": 1.0
    }

    for f in findings:
        sev = f.get("severity", "MEDIUM").upper()
        s_weight = sev_map.get(sev, 2.0)
        
        cat = f.get("category", "")
        i_weight = cat_impact_map.get(cat, 1.0)
        
        conf = f.get("confidence", 0.8)
        evidence_len = len(f.get("evidence", []))
        e_weight = min(1.5, 0.8 + (evidence_len * 0.15))

        # Priority calculation
        priority_score = round(s_weight * i_weight * e_weight * conf * 10, 2)
        
        item = dict(f)
        item["priority_score"] = priority_score
        prioritized.append(item)

    prioritized.sort(key=lambda x: x["priority_score"], reverse=True)
    return prioritized
