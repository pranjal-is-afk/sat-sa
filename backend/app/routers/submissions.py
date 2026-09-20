"""
Submissions & Ingestion Router
Handles periodic multi-file CSV/JSON uploads, SHA-256 calculation,
data-quality checks, and ingestion batch approval.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List, Optional
import sqlite3

from backend.app.database.connection import get_db
from backend.app.services.ingestion_service import process_submission_files

router = APIRouter(prefix="/submissions", tags=["Submissions"])

@router.get("")
def list_submissions(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        SELECT s.*, c.name as entity_name, c.sector
        FROM submission s
        JOIN cse c ON s.cse_id = c.cse_id
        ORDER BY s.uploaded_at DESC
    """)
    rows = cursor.fetchall()
    return [dict(r) for r in rows]

@router.get("/{submission_id}/validation")
def get_submission_validation(submission_id: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM submission WHERE submission_id = ?", (submission_id,))
    sub = cursor.fetchone()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    cursor.execute("SELECT * FROM submission_file WHERE submission_id = ?", (submission_id,))
    files = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM data_quality_issue WHERE submission_id = ?", (submission_id,))
    issues = [dict(r) for r in cursor.fetchall()]

    return {
        "submission": dict(sub),
        "files": files,
        "data_quality_issues": issues,
        "summary": {
            "total_files": len(files),
            "total_issues": len(issues),
            "errors": len([i for i in issues if i["severity"] == "ERROR"]),
            "warnings": len([i for i in issues if i["severity"] == "WARNING"])
        }
    }

@router.post("/upload")
async def upload_submission_files(
    cse_id: str = Form(...),
    reporting_period: str = Form("2026-Q3"),
    uploader_id: str = Form("ADMIN-01"),
    files: List[UploadFile] = File(...),
    db: sqlite3.Connection = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    # Read bytes for each file
    payload = []
    for f in files:
        content = await f.read()
        payload.append((f.filename, content))

    try:
        result = process_submission_files(
            conn=db,
            cse_id=cse_id,
            reporting_period=reporting_period,
            uploader_id=uploader_id,
            files_payload=payload
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion processing error: {str(e)}")
