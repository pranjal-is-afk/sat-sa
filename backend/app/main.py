"""
Main FastAPI Application Entrypoint
Mounts all REST routers, configures offline security headers,
and serves the standalone air-gapped web console.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.app.config import APP_VERSION, RULE_VERSION, BASE_DIR
from backend.app.database.schema import init_db
from backend.app.routers import (
    auth,
    entities,
    findings,
    submissions,
    analytics,
    peer_groups,
    reports,
    audit,
    admin
)

app = FastAPI(
    title="SAT-SA: Supervisory Analytics Tool for SOC Assessment",
    description="Offline, explainable, evidence-first supervisory analytics platform for NCIIPC examiners.",
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Enclave local CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(entities.router, prefix="/api/v1")
app.include_router(findings.router, prefix="/api/v1")
app.include_router(submissions.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(peer_groups.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# Mount Frontend Static Assets
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

@app.on_event("startup")
def on_startup():
    init_db()
    print(f"SAT-SA Backend Initialized. Enclave Mode: AIR-GAPPED. Version: {APP_VERSION}")
