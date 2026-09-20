"""
Application Configuration for SAT-SA
Air-gapped and offline default settings.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sat_sa.db"
UPLOAD_DIR = DATA_DIR / "uploads"
RAW_DIR = DATA_DIR / "raw"
SAMPLE_DIR = DATA_DIR / "sample"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
RAW_DIR.mkdir(exist_ok=True)

# Security & Versions
APP_VERSION = "1.0.0"
RULE_VERSION = "1.2.0"
OFFLINE_MODE = True
AIR_GAPPED = True
SECRET_KEY = "ENCLAVE_OFFLINE_SECRET_KEY_NCIIPC_2026"
SESSION_EXPIRY_HOURS = 12
