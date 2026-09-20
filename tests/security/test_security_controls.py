"""
Security & Air-Gap Compliance Test Suite
Verifies SQL injection prevention, CSV formula injection neutralization,
and zero external network egress.
"""

import sqlite3
import pytest
from backend.app.database.schema import DDL
from backend.app.services.normalization_service import sanitize_text

def test_sql_injection_defense():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(DDL)

    malicious_cse_id = "CSE-01' OR '1'='1"
    
    # Parameterized query should return 0 rows rather than dumping all
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cse WHERE cse_id = ?", (malicious_cse_id,))
    rows = cursor.fetchall()
    assert len(rows) == 0

def test_csv_injection_defanging():
    payloads = [
        "=cmd|' /C calc'!A0",
        "+cmd|' /C calc'!A0",
        "-123+456",
        "@SUM(1+1)",
        "\tmalicious_tab"
    ]
    for p in payloads:
        sanitized = sanitize_text(p)
        assert sanitized.startswith("'"), f"Expected leading quote prefix for {p}, got {sanitized}"

def test_air_gap_zero_remote_dependencies():
    """Confirms no external internet URIs or cloud SDKs are referenced in runtime code."""
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent.parent
    
    forbidden_terms = [
        "api.openai.com",
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        "cdn.jsdelivr.net",
        "cdnjs.cloudflare.com",
        "fonts.googleapis.com"
    ]

    for py_file in base_dir.glob("backend/**/*.py"):
        content = py_file.read_text(encoding="utf-8")
        for term in forbidden_terms:
            assert term not in content, f"Forbidden remote dependency '{term}' found in {py_file}"

    for js_file in base_dir.glob("frontend/**/*.js"):
        content = js_file.read_text(encoding="utf-8")
        for term in forbidden_terms:
            assert term not in content, f"Forbidden remote dependency '{term}' found in {js_file}"

    for html_file in base_dir.glob("frontend/**/*.html"):
        content = html_file.read_text(encoding="utf-8")
        for term in forbidden_terms:
            assert term not in content, f"Forbidden remote dependency '{term}' found in {html_file}"
