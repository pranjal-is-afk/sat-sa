"""
Local RBAC Authentication Router
Provides offline local authentication for examiners, admins, and auditors.
"""

from fastapi import APIRouter, HTTPException, status
from backend.app.models.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Local enclave accounts for offline evaluation
LOCAL_USERS = {
    "examiner": {"password": "password123", "role": "Supervisory Examiner"},
    "lead_supervisor": {"password": "password123", "role": "Lead Supervisor"},
    "data_admin": {"password": "password123", "role": "Data Administrator"},
    "system_admin": {"password": "password123", "role": "System Administrator"},
    "auditor": {"password": "password123", "role": "Auditor"}
}

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    user = LOCAL_USERS.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid enclave credentials."
        )
    return LoginResponse(
        token=f"ENCLAVE_LOCAL_TOKEN_{payload.username.upper()}_2026",
        username=payload.username,
        role=user["role"],
        expires_in_hours=12
    )

@router.get("/me")
def get_current_user():
    return {
        "username": "examiner",
        "role": "Supervisory Examiner",
        "enclave_access": "GRANTED",
        "air_gap_status": "OFFLINE_VERIFIED"
    }
