"""
Cryptographic Audit Logging Service
Implements immutable append-only audit trail with SHA-256 hash chaining.
Every event hash = SHA256(prev_hash | timestamp | action | user_id | payload)
"""

import json
import hashlib
from datetime import datetime, timezone
import sqlite3
from typing import Dict, Any, List

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

def log_audit_event(
    conn: sqlite3.Connection,
    action: str,
    user_id: str,
    payload: Dict[str, Any]
) -> str:
    """Appends an event and returns the new cryptographic hash."""
    cursor = conn.cursor()
    cursor.execute("SELECT hash FROM audit_events ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    prev_hash = row["hash"] if row else GENESIS_HASH

    timestamp = datetime.now(timezone.utc).isoformat()
    serialized_payload = json.dumps(payload, sort_keys=True)

    block_data = f"{prev_hash}|{timestamp}|{action}|{user_id}|{serialized_payload}"
    curr_hash = hashlib.sha256(block_data.encode("utf-8")).hexdigest()

    cursor.execute(
        "INSERT INTO audit_events (timestamp, action, user_id, payload, prev_hash, hash) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (timestamp, action, user_id, serialized_payload, prev_hash, curr_hash)
    )
    conn.commit()
    return curr_hash

def get_audit_trail(conn: sqlite3.Connection, limit: int = 100) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    events = []
    for r in rows:
        events.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "action": r["action"],
            "user_id": r["user_id"],
            "payload": json.loads(r["payload"]),
            "prev_hash": r["prev_hash"],
            "hash": r["hash"]
        })
    return events

def verify_audit_integrity(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Verifies that no record has been tampered with or deleted from the chain."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_events ORDER BY id ASC")
    rows = cursor.fetchall()

    if not rows:
        return {"valid": True, "total_events": 0, "message": "Audit trail is empty."}

    expected_prev = GENESIS_HASH
    for idx, r in enumerate(rows):
        if r["prev_hash"] != expected_prev:
            return {
                "valid": False,
                "broken_at_id": r["id"],
                "reason": f"Hash chain broken at record {r['id']}: expected prev_hash {expected_prev}, got {r['prev_hash']}"
            }
        
        block_data = f"{r['prev_hash']}|{r['timestamp']}|{r['action']}|{r['user_id']}|{r['payload']}"
        recalculated_hash = hashlib.sha256(block_data.encode("utf-8")).hexdigest()
        
        if r["hash"] != recalculated_hash:
            return {
                "valid": False,
                "broken_at_id": r["id"],
                "reason": f"Payload tampering detected at record {r['id']}: recalculated hash does not match stored hash."
            }
        
        expected_prev = r["hash"]

    return {
        "valid": True,
        "total_events": len(rows),
        "latest_hash": expected_prev,
        "message": "Cryptographic audit chain is 100% intact and untampered."
    }
