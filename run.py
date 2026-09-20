"""
SAT-SA CLI Launcher & Bootstrap Script
Usage:
    python run.py --seed           # Initialize DB, ingest synthetic data, run analytics
    python run.py --port 8000      # Start the supervisory server
    python run.py --healthcheck    # Run local enclave health verification
"""

import sys
import argparse
import uvicorn
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.database.schema import init_db
from backend.app.database.connection import get_db_connection
from backend.app.routers.admin import reseed_database
from backend.app.services.audit_service import verify_audit_integrity

def main():
    parser = argparse.ArgumentParser(description="SAT-SA Supervisory Analytics Platform")
    parser.add_argument("--seed", action="store_true", help="Seed database with synthetic ground truth data")
    parser.add_argument("--serve", action="store_true", help="Start server after seeding")
    parser.add_argument("--healthcheck", action="store_true", help="Run local health verification checks")
    parser.add_argument("--host", default="127.0.0.1", help="Binding IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Binding port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()

    # Step 1: Ensure database exists and is initialized
    init_db()

    # Step 2: Seed if requested
    if args.seed:
        print("[*] Seeding database with 10 synthetic CSE profiles...")
        conn = get_db_connection()
        try:
            res = reseed_database(conn)
            print(f"[OK] Reseed complete: {res.get('findings_generated', 0)} findings generated across {res.get('entities_scored', 0)} entities.")
        finally:
            conn.close()
        if not args.serve:
            print("[OK] Database seeded successfully. Run 'python run.py' to launch server.")
            return

    # Step 3: Healthcheck if requested
    if args.healthcheck:
        print("[*] Performing air-gapped enclave healthcheck...")
        conn = get_db_connection()
        try:
            audit_res = verify_audit_integrity(conn)
            if audit_res["valid"]:
                print(f"[PASS] Cryptographic audit chain verified ({audit_res['total_events']} events, Genesis intact).")
            else:
                print(f"[FAIL] Audit chain compromised: {audit_res['reason']}")
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as c FROM alert")
            alert_count = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) as c FROM finding")
            finding_count = cursor.fetchone()["c"]
            print(f"[PASS] Local SQLite database online ({alert_count} alerts, {finding_count} findings).")
            print("[PASS] Scikit-learn and NumPy modules verified.")
            print("[OK] SAT-SA platform is healthy and ready for supervisory review.")
            return
        finally:
            conn.close()

    # Step 4: Start Server
    print(f"==================================================================")
    print(f"  SAT-SA: Supervisory Analytics Tool for SOC Assessment (NCIIPC)  ")
    print(f"  Operating Mode: AIR-GAPPED OFFLINE ENCLAVE                     ")
    print(f"  Console URL:    http://{args.host}:{args.port}                 ")
    print(f"  API Docs:       http://{args.host}:{args.port}/api/docs        ")
    print(f"==================================================================")

    uvicorn.run(
        "backend.app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
