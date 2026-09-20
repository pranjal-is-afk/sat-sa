"""
Integration Test for End-to-End Submission, Validation, Analytics, and Disposition Flow
"""

import sqlite3
import pytest
from backend.app.database.schema import DDL
from backend.app.services.ingestion_service import process_submission_files
from backend.app.routers.analytics import trigger_analytics_run
from backend.app.routers.findings import record_disposition
from backend.app.models.schemas import DispositionRequest

@pytest.fixture
def test_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(DDL)
    # Seed mock CSE
    conn.execute("INSERT INTO cse (cse_id, name, sector, criticality_tier) VALUES ('CSE-TEST', 'Test Infrastructure', 'Energy', 'Tier-1')")
    conn.commit()
    return conn

def test_full_pipeline_flow(test_db):
    # 1. Prepare sample CSV payloads
    alerts_csv = """alert_id,cse_id,created_at,acknowledged_at,closed_at,severity,alert_category,asset_id,status,case_id
ALT-INT-1,CSE-TEST,2026-08-01T10:00:00Z,2026-08-01T10:02:00Z,2026-08-01T10:04:00Z,Critical,Malware,AST-INT-1,Closed,CASE-INT-1
"""
    cases_csv = """case_id,cse_id,alert_id,created_at,closed_at,investigation_summary,evidence_count
CASE-INT-1,CSE-TEST,ALT-INT-1,2026-08-01T10:00:00Z,2026-08-01T10:04:00Z,Fast close,0
"""
    assets_csv = """asset_id,cse_id,asset_type,business_service,criticality,monitoring_expected
AST-INT-1,CSE-TEST,SCADA,Grid Control,Critical,True
AST-SILENT-1,CSE-TEST,Database,Customer DB,Critical,True
"""
    cov_csv = """asset_id,cse_id,period,expected_event_volume,observed_event_volume,coverage_status
AST-INT-1,CSE-TEST,2026-Q3,1000,1200,Active
AST-SILENT-1,CSE-TEST,2026-Q3,1000,0,Silent
"""

    files = [
        ("alerts.csv", alerts_csv.encode("utf-8")),
        ("cases.csv", cases_csv.encode("utf-8")),
        ("assets.csv", assets_csv.encode("utf-8")),
        ("telemetry_coverage.csv", cov_csv.encode("utf-8"))
    ]

    # 2. Ingest
    ingest_res = process_submission_files(test_db, "CSE-TEST", "2026-Q3", "TEST-ADMIN", files)
    assert ingest_res["status"] == "VALIDATED"
    assert ingest_res["valid_alerts_count"] == 1
    assert ingest_res["valid_cases_count"] == 1

    # 3. Trigger Analytics
    analytics_res = trigger_analytics_run("CSE-TEST", test_db)
    assert analytics_res["status"] == "COMPLETED"
    assert analytics_res["total_findings"] >= 2 # Should detect fast closure, missing escalation, and negative space

    # 4. Record Human Supervisor Disposition
    cursor = test_db.cursor()
    cursor.execute("SELECT finding_id FROM finding WHERE cse_id = 'CSE-TEST' LIMIT 1")
    finding_id = cursor.fetchone()["finding_id"]

    disp_req = DispositionRequest(
        decision="Confirmed",
        comment="Verified critical fast closure with 0 evidence in audit.",
        reviewer_id="EXAMINER-INT"
    )
    disp_res = record_disposition(finding_id, disp_req, test_db)
    assert disp_res["status"] == "CONFIRMED"
    assert "audit_hash" in disp_res
