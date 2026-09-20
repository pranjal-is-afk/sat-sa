"""
Analytics Pipeline Router
Executes supervisory analytics, computes findings,
and persists decomposed entity risk scores.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3
import json
from typing import Optional

from backend.app.database.connection import get_db
from backend.app.services.audit_service import log_audit_event
from analytics.engine import SupervisoryAnalyticsEngine

router = APIRouter(prefix="/analytics", tags=["Supervisory Analytics"])

@router.post("/run")
def trigger_analytics_run(
    cse_id: Optional[str] = Query(None),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()

    # Load canonical records from SQLite
    if cse_id:
        cursor.execute("SELECT * FROM alert WHERE cse_id = ?", (cse_id,))
        alerts = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT * FROM incident_case WHERE cse_id = ?", (cse_id,))
        cases = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT * FROM asset WHERE cse_id = ?", (cse_id,))
        assets = [dict(r) for r in cursor.fetchall()]
    else:
        cursor.execute("SELECT * FROM alert")
        alerts = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT * FROM incident_case")
        cases = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT * FROM asset")
        assets = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM investigation_step")
    steps = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM escalation")
    escalations = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM remediation")
    remediations = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM telemetry_coverage")
    coverage = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM data_quality_issue")
    dq_issues = [dict(r) for r in cursor.fetchall()]

    engine = SupervisoryAnalyticsEngine()
    results = engine.run_pipeline(
        alerts=alerts,
        cases=cases,
        assets=assets,
        steps=steps,
        escalations=escalations,
        remediations=remediations,
        telemetry_coverage=coverage,
        data_quality_issues=dq_issues
    )

    # Persist findings to database
    for f in results["findings"]:
        cursor.execute("""
            INSERT OR REPLACE INTO finding (
                finding_id, cse_id, rule_id, rule_version, category, type,
                severity, confidence, status, case_id, alert_id, asset_id,
                reason, evidence_json, peer_baseline, recommended_action, priority_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f["finding_id"], f["entity_id"], f["rule_id"], f["rule_version"],
            f["category"], f["type"], f["severity"], f["confidence"],
            f.get("status", "OPEN"), f.get("case_id"), f.get("alert_id"), f.get("asset_id"),
            f["reason"], json.dumps(f["evidence"]), f.get("peer_baseline", ""),
            f["recommended_action"], f.get("priority_score", 10.0)
        ))

    # Persist decomposed entity risk scores
    for eid, risk in results["entity_risks"].items():
        cursor.execute("""
            INSERT OR REPLACE INTO entity_supervisory_risk (
                cse_id, score, risk_tier, sub_scores_json, contributors_json, findings_count
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            eid, risk["score"], risk["risk_tier"],
            json.dumps(risk["sub_scores"]),
            json.dumps(risk["contributors"]),
            risk["findings_count"]
        ))

    db.commit()

    # Log to audit trail
    log_audit_event(
        db,
        action="SUPERVISORY_ANALYTICS_EXECUTED",
        user_id="SUPERVISOR-AUTO",
        payload={
            "cse_filter": cse_id or "ALL",
            "total_findings_generated": results["total_findings"],
            "entities_scored": len(results["entity_risks"])
        }
    )

    return {
        "status": "COMPLETED",
        "total_findings": results["total_findings"],
        "entities_evaluated": len(results["entity_risks"]),
        "peer_metrics": results["peer_metrics"]
    }
