"""
Cryptographic Audit Router
Provides read-only access to append-only audit trail and runs hash chain integrity verification.
"""

from fastapi import APIRouter, Depends, Query
import sqlite3

from backend.app.database.connection import get_db
from backend.app.services.audit_service import get_audit_trail, verify_audit_integrity

router = APIRouter(prefix="/audit-events", tags=["Audit & Provenance"])

@router.get("")
def list_audit_events(
    limit: int = Query(100),
    db: sqlite3.Connection = Depends(get_db)
):
    return get_audit_trail(db, limit=limit)

@router.get("/verify-integrity")
def check_chain_integrity(db: sqlite3.Connection = Depends(get_db)):
    """Verifies SHA-256 hash chaining from Genesis block to latest event."""
    return verify_audit_integrity(db)
