"""
Peer Groups & Benchmarking Router
Provides sector cohorts and statistical distributions for peer comparison.
"""

from fastapi import APIRouter, Depends
import sqlite3
from typing import Dict, Any

from backend.app.database.connection import get_db

router = APIRouter(prefix="/peer-groups", tags=["Peer Benchmarks"])

@router.get("")
def get_peer_groups(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        SELECT sector, COUNT(*) as entity_count,
               AVG(COALESCE(r.score, 0)) as avg_risk_score
        FROM cse c
        LEFT JOIN entity_supervisory_risk r ON c.cse_id = r.cse_id
        GROUP BY sector
    """)
    rows = cursor.fetchall()
    return [dict(r) for r in rows]

@router.get("/metrics")
def get_peer_metrics():
    return {
        "Energy & Power": {
            "median_closure_time_mins": 58.4,
            "peer_p05_closure_time_mins": 14.2,
            "escalation_compliance_rate": 0.982,
            "average_evidence_density": 3.4,
            "repeat_alert_threshold": 0.20
        },
        "Banking & Finance": {
            "median_closure_time_mins": 45.0,
            "peer_p05_closure_time_mins": 18.0,
            "escalation_compliance_rate": 0.995,
            "average_evidence_density": 4.1,
            "repeat_alert_threshold": 0.15
        },
        "Transportation": {
            "median_closure_time_mins": 62.0,
            "peer_p05_closure_time_mins": 12.0,
            "escalation_compliance_rate": 0.970,
            "average_evidence_density": 2.8,
            "repeat_alert_threshold": 0.22
        },
        "Defense & Space": {
            "median_closure_time_mins": 75.0,
            "peer_p05_closure_time_mins": 25.0,
            "escalation_compliance_rate": 0.998,
            "average_evidence_density": 4.5,
            "repeat_alert_threshold": 0.10
        }
    }
