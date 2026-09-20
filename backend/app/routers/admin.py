"""
System Administration & Health Router
"""

from fastapi import APIRouter, Depends
import sqlite3
import os
import csv
from pathlib import Path

from backend.app.database.connection import get_db
from backend.app.config import APP_VERSION, RULE_VERSION, AIR_GAPPED, BASE_DIR
from backend.app.services.ingestion_service import process_submission_files
from backend.app.routers.analytics import trigger_analytics_run

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.get("/health")
def healthcheck(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchone()
    return {
        "status": "HEALTHY",
        "air_gapped": AIR_GAPPED,
        "app_version": APP_VERSION,
        "rule_version": RULE_VERSION,
        "enclave_mode": "Isolated NCIIPC Subnet",
        "database": "SQLite WAL Mode Active"
    }

@router.get("/stats")
def system_stats(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    def count(tbl):
        try:
            cursor.execute(f"SELECT COUNT(*) as c FROM {tbl}")
            return cursor.fetchone()["c"]
        except Exception:
            return 0

    return {
        "cses": count("cse"),
        "submissions": count("submission"),
        "alerts": count("alert"),
        "cases": count("incident_case"),
        "assets": count("asset"),
        "steps": count("investigation_step"),
        "escalations": count("escalation"),
        "findings": count("finding"),
        "dispositions": count("finding_disposition"),
        "audit_events": count("audit_events")
    }

@router.post("/reseed")
def reseed_database(db: sqlite3.Connection = Depends(get_db)):
    """Reseeds database from synthetic CSV files and runs analytics."""
    sample_dir = BASE_DIR / "data" / "sample"
    if not (sample_dir / "alerts.csv").exists():
        return {"status": "ERROR", "message": "Sample CSVs not found. Run generator first."}

    # Populate CSEs
    cses = [
        ("ALL_CSES", "National Infrastructure Assessment Repository", "Multi-Sector", "National"),
        ("CSE-01", "Northern Power Grid Corp", "Energy & Power", "Tier-1"),
        ("CSE-02", "Apex Federal Reserve Bank", "Banking & Finance", "Tier-1"),
        ("CSE-03", "National Telecom Backbone", "Telecommunications", "Tier-1"),
        ("CSE-04", "National Freight Rail Dispatch", "Transportation", "Tier-1"),
        ("CSE-05", "Strategic Defense Electronics", "Defense & Space", "Tier-1"),
        ("CSE-06", "Kalpakkam Atomic Energy Station", "Nuclear Energy", "Tier-1"),
        ("CSE-07", "Trans-National Petroleum Pipeline", "Oil & Gas", "Tier-1"),
        ("CSE-08", "Metropolitan Water Authority", "Water & Sanitation", "Tier-2"),
        ("CSE-09", "Regional Smart Grid Distribution", "Energy & Power", "Tier-2"),
        ("CSE-10", "Air Cargo & Logistics Network", "Transportation", "Tier-1"),
    ]
    cursor = db.cursor()
    for cid, name, sec, tier in cses:
        cursor.execute("""
            INSERT OR REPLACE INTO cse (cse_id, name, sector, criticality_tier)
            VALUES (?, ?, ?, ?)
        """, (cid, name, sec, tier))
    db.commit()

    # Ingest files
    filenames = ["alerts.csv", "cases.csv", "assets.csv", "investigation_steps.csv", "escalations.csv", "remediations.csv", "telemetry_coverage.csv"]
    payload = []
    for fn in filenames:
        fp = sample_dir / fn
        if fp.exists():
            with open(fp, "rb") as f:
                payload.append((fn, f.read()))

    process_submission_files(db, "ALL_CSES", "2026-Q3", "SUPERVISORY_SEED", payload)
    
    # Run analytics
    res = trigger_analytics_run(None, db)

    return {
        "status": "RESEEDED",
        "findings_generated": res["total_findings"],
        "entities_scored": res["entities_evaluated"]
    }
