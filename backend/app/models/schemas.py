"""
Pydantic Request and Response Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    username: str
    role: str
    expires_in_hours: int

class DispositionRequest(BaseModel):
    decision: str = Field(..., description="Confirmed, Not Substantiated, False Positive, Needs More Evidence, Remediation Required")
    comment: str = Field(..., min_length=5, description="Mandatory supervisor rationale")
    reviewer_id: Optional[str] = "EXAMINER-01"

class FindingResponse(BaseModel):
    finding_id: str
    cse_id: str
    rule_id: str
    rule_version: str
    category: str
    type: str
    severity: str
    confidence: float
    status: str
    case_id: Optional[str] = None
    alert_id: Optional[str] = None
    asset_id: Optional[str] = None
    reason: str
    evidence: List[Dict[str, Any]]
    peer_baseline: Optional[str] = None
    recommended_action: str
    priority_score: float
    created_at: str

class EntityRiskResponse(BaseModel):
    cse_id: str
    name: str
    sector: str
    criticality_tier: str
    score: float
    risk_tier: str
    sub_scores: Dict[str, float]
    contributors: List[Dict[str, Any]]
    findings_count: int

class AuditEventResponse(BaseModel):
    id: int
    timestamp: str
    action: str
    user_id: str
    payload: Dict[str, Any]
    prev_hash: str
    hash: str

class ReportRequest(BaseModel):
    cse_id: Optional[str] = None
    format: str = "HTML" # HTML or JSON
