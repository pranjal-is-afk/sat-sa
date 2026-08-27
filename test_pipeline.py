import os
import sys
import glob
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath('.'))

from backend.main import app
from backend.db import engine
from backend.models.orm import Base

def run_e2e_test():
    print("=== STARTING SAT-SA E2E VERIFICATION TEST ===")
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[1] Database initialized.")
    
    client = TestClient(app)
    
    sample_files = glob.glob("data/sample/*.csv")
    print(f"[2] Found {len(sample_files)} sample CSV files to ingest...")
    
    files_payload = []
    file_handles = []
    try:
        for fpath in sample_files:
            fname = os.path.basename(fpath)
            fh = open(fpath, "rb")
            file_handles.append(fh)
            files_payload.append(("files", (fname, fh, "text/csv")))
            
        res = client.post("/api/ingest", files=files_payload)
        assert res.status_code == 200, f"Ingest failed: {res.text}"
        ingest_data = res.json()
        batch_id = ingest_data.get("batch_id")
        print(f"    Ingest successful! Batch ID: {batch_id}")
        print(f"    Records parsed: {ingest_data.get('records_parsed')}")
        print(f"    Errors count: {len(ingest_data.get('errors', []))}")
        print(f"    Warnings count: {len(ingest_data.get('warnings', []))}")
    finally:
        for fh in file_handles:
            fh.close()
            
    print(f"[3] Triggering /api/analyse for batch {batch_id}...")
    import time
    start_time = time.time()
    res = client.post("/api/analyse", json={"batch_id": batch_id})
    elapsed = time.time() - start_time
    assert res.status_code == 200, f"Analyse failed: {res.text}"
    print(f"    Analysis completed in {elapsed:.2f} seconds! (PRD target: < 30s)")
    
    print("[4] Checking /api/overview...")
    res = client.get(f"/api/overview?batch_id={batch_id}")
    assert res.status_code == 200
    overview = res.json()
    print(f"    Total CSEs: {overview['cse_count']}")
    print(f"    Total alerts: {overview['alert_count']}")
    print(f"    Entities requiring attention (score >= 50): {overview['entities_requiring_attention']}")
    print(f"    Negative space findings count: {overview['negative_space_count']}")
    print(f"    Risk distribution: {overview['risk_distribution']}")
    print(f"    Top risks: {overview['top_risks']}")
    
    print("[5] Checking /api/entities and verifying score ordering: CSE-07 > CSE-11 > CSE-01...")
    res = client.get(f"/api/entities?batch_id={batch_id}")
    assert res.status_code == 200
    entities = res.json()
    scores = {e["cse_id"]: e["risk_score"] for e in entities}
    print(f"    Entity Scores: {scores}")
    
    score_07 = scores.get("CSE-07", 0)
    score_11 = scores.get("CSE-11", 0)
    score_01 = scores.get("CSE-01", 0)
    
    print(f"    CSE-07 Risk Score: {score_07}")
    print(f"    CSE-11 Risk Score: {score_11}")
    print(f"    CSE-01 Risk Score: {score_01}")
    
    assert score_07 > score_11, f"Expected CSE-07 ({score_07}) > CSE-11 ({score_11})"
    assert score_11 > score_01, f"Expected CSE-11 ({score_11}) > CSE-01 ({score_01})"
    print("    [PASS] Risk score ordering satisfied: CSE-07 > CSE-11 > CSE-01!")
    
    print("[6] Checking CSE-07 Dossier for execution gap flags...")
    res = client.get(f"/api/entity/CSE-07?batch_id={batch_id}")
    assert res.status_code == 200
    dossier_07 = res.json()
    rule_ids_07 = [f["rule_id"] for f in dossier_07.get("flags", [])]
    print(f"    CSE-07 Flags: {rule_ids_07}")
    
    assert "R-02" in rule_ids_07, "Missing R-02 (Fast closure) flag for CSE-07"
    assert "R-03" in rule_ids_07, "Missing R-03 (Low escalation) flag for CSE-07"
    assert "R-04" in rule_ids_07, "Missing R-04 (Template text) flag for CSE-07"
    
    r02_flag = next(f for f in dossier_07["flags"] if f["rule_id"] == "R-02")
    assert len(r02_flag.get("evidence_ids", [])) > 0, "R-02 should cite evidence IDs"
    print(f"    R-02 cited {len(r02_flag['evidence_ids'])} alert IDs (e.g. {r02_flag['evidence_ids'][:3]})")
    print("    [PASS] CSE-07 execution gap flags verified with cited evidence!")
    
    print("[7] Checking CSE-11 Dossier for negative space findings...")
    res = client.get(f"/api/entity/CSE-11?batch_id={batch_id}")
    assert res.status_code == 200
    dossier_11 = res.json()
    ns_findings_11 = dossier_11.get("negative_space_findings", [])
    print(f"    CSE-11 Negative space findings: {[f['description'] for f in ns_findings_11]}")
    
    has_silent_fin = any("FIN-SERVER-04" in f.get("description", "") or f.get("asset_id") == "FIN-SERVER-04" for f in ns_findings_11)
    has_missing_high = any("HIGH" in f.get("description", "") or f.get("type") == "MISSING_ALERT_CATEGORY" for f in ns_findings_11)
    
    assert has_silent_fin, "Missing FIN-SERVER-04 negative space finding for CSE-11"
    assert has_missing_high, "Missing HIGH alert category negative space finding for CSE-11"
    print("    [PASS] CSE-11 negative space findings verified!")
    
    print("[8] Checking /api/negative-space endpoint...")
    res = client.get(f"/api/negative-space?batch_id={batch_id}")
    assert res.status_code == 200
    ns_list = res.json()
    print(f"    Total batch negative space findings: {len(ns_list)}")
    assert len(ns_list) >= 3, f"Expected >= 3 negative space findings, got {len(ns_list)}"
    print("    [PASS] Batch negative space count verified!")
    
    print("[9] Testing Grey Status for low-volume entity (<50 records)...")
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix="_alerts.csv", delete=False) as tf:
        tf.write("alert_id,cse_id,severity,created_at,acknowledged_at,closed_at,status,case_id,asset_id,escalated\n")
        for i in range(15):
            tf.write(f"ALT-CSE-99-{i:03d},CSE-99,MEDIUM,2024-10-15T10:00:00,2024-10-15T10:05:00,2024-10-15T10:30:00,CLOSED,,,False\n")
        tf_path = tf.name
        
    try:
        with open(tf_path, "rb") as fh:
            res = client.post("/api/ingest", files=[("files", ("CSE-99_alerts.csv", fh, "text/csv"))])
        batch_id_grey = res.json()["batch_id"]
        res = client.post("/api/analyse", json={"batch_id": batch_id_grey})
        res = client.get(f"/api/entities?batch_id={batch_id_grey}")
        entities_grey = res.json()
        cse_99 = next(e for e in entities_grey if e["cse_id"] == "CSE-99")
        print(f"    CSE-99 Risk Level: {cse_99['risk_level']}, is_grey: {cse_99['is_grey']}")
        assert cse_99["is_grey"] is True, "CSE-99 should be is_grey=True"
        assert cse_99["risk_level"] == "UNASSESSED", "CSE-99 should be UNASSESSED"
        print("    [PASS] Grey status verified!")
    finally:
        os.remove(tf_path)
        
    print("\n=======================================================")
    print("  ALL ACCEPTANCE CRITERIA PASSED SUCCESSFULLY! (100%)  ")
    print("=======================================================\n")

if __name__ == "__main__":
    run_e2e_test()
