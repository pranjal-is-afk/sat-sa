"""
Unit Tests for Cryptographic Audit Trail Chaining & Integrity Verification
"""

import sqlite3
import pytest
from backend.app.services.audit_service import log_audit_event, verify_audit_integrity, get_audit_trail

@pytest.fixture
def memory_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,
            user_id TEXT NOT NULL,
            payload TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            hash TEXT NOT NULL
        )
    """)
    return conn

def test_audit_hash_chaining(memory_db):
    h1 = log_audit_event(memory_db, "LOGIN", "EXAMINER-1", {"ip": "127.0.0.1"})
    h2 = log_audit_event(memory_db, "DISPOSITION", "EXAMINER-1", {"finding_id": "F-001", "decision": "Confirmed"})
    h3 = log_audit_event(memory_db, "REPORT_EXPORT", "LEAD-DIR", {"report_id": "REP-2026-01"})

    assert len(h1) == 64
    assert len(h2) == 64
    assert len(h3) == 64
    assert h1 != h2 != h3

    # Verification should pass
    result = verify_audit_integrity(memory_db)
    assert result["valid"] is True
    assert result["total_events"] == 3
    assert result["latest_hash"] == h3

def test_audit_tamper_detection(memory_db):
    log_audit_event(memory_db, "ACTION-1", "USER-1", {"val": 100})
    log_audit_event(memory_db, "ACTION-2", "USER-2", {"val": 200})
    log_audit_event(memory_db, "ACTION-3", "USER-3", {"val": 300})

    # Tamper with row 2's payload maliciously
    memory_db.execute("UPDATE audit_events SET payload = '{\"val\": 999}' WHERE id = 2")
    memory_db.commit()

    # Verification must detect the tampering
    result = verify_audit_integrity(memory_db)
    assert result["valid"] is False
    assert result["broken_at_id"] == 2
    assert "tampering detected" in result["reason"]
