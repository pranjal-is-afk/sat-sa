"""
Supervisory Reports Router
Generates executive reports, evidence packages, and downloadable HTML/JSON.
"""

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import HTMLResponse
import sqlite3
from typing import Optional

from backend.app.database.connection import get_db
from backend.app.services.report_service import generate_supervisory_report, render_html_report

router = APIRouter(prefix="/reports", tags=["Reporting"])

@router.get("/json")
def get_report_json(
    cse_id: Optional[str] = Query(None),
    db: sqlite3.Connection = Depends(get_db)
):
    report_data = generate_supervisory_report(db, cse_id=cse_id)
    return report_data

@router.get("/html", response_class=HTMLResponse)
def get_report_html(
    cse_id: Optional[str] = Query(None),
    db: sqlite3.Connection = Depends(get_db)
):
    report_data = generate_supervisory_report(db, cse_id=cse_id)
    html_content = render_html_report(report_data)
    return HTMLResponse(content=html_content, status_code=200)
