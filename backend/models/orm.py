from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, Text
from ..db import Base

class BatchRecord(Base):
    __tablename__ = 'batches'
    id = Column(String, primary_key=True)
    created_at = Column(DateTime)
    cse_ids = Column(String)
    status = Column(String)

class AlertRecord(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String)
    alert_id = Column(String)
    cse_id = Column(String)
    severity = Column(String)
    created_at = Column(DateTime)
    acknowledged_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    status = Column(String)
    case_id = Column(String, nullable=True)
    asset_id = Column(String, nullable=True)
    escalated = Column(Boolean, nullable=True)
    closure_minutes = Column(Float, nullable=True)

class CaseRecord(Base):
    __tablename__ = 'cases'
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String)
    case_id = Column(String)
    cse_id = Column(String)
    opened_at = Column(DateTime)
    closed_at = Column(DateTime, nullable=True)
    investigation_text = Column(Text, nullable=True)
    investigator_id = Column(String, nullable=True)
    escalated = Column(Boolean, nullable=True)
    resolution = Column(String, nullable=True)
    alert_ids = Column(String, nullable=True)

class AssetRecord(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String)
    asset_id = Column(String)
    cse_id = Column(String)
    classification = Column(String)
    asset_type = Column(String, nullable=True)
    sector = Column(String, nullable=True)

class CSEFeatures(Base):
    __tablename__ = 'cse_features'
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String)
    cse_id = Column(String)
    features_json = Column(Text)
    sector = Column(String, nullable=True)
    alert_count = Column(Integer)
    case_count = Column(Integer)

class RiskScore(Base):
    __tablename__ = 'risk_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String)
    cse_id = Column(String)
    risk_score = Column(Float)
    risk_level = Column(String)
    score_breakdown_json = Column(Text)
    shap_values_json = Column(Text)
    is_grey = Column(Boolean)
    primary_reason = Column(String, nullable=True)
    flag_count = Column(Integer)
    analysed_at = Column(DateTime)

class FlagRecord(Base):
    __tablename__ = 'flags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String)
    cse_id = Column(String)
    rule_id = Column(String)
    rule_name = Column(String)
    description = Column(Text)
    severity = Column(String)
    flag_type = Column(String)
    evidence_ids_json = Column(Text)

class NegativeSpaceFinding(Base):
    __tablename__ = 'negative_space_findings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String)
    cse_id = Column(String)
    finding_type = Column(String)
    asset_id = Column(String, nullable=True)
    description = Column(Text)
    expected_value = Column(String)
    observed_value = Column(String)
    severity = Column(String)
    peer_context_json = Column(Text)

class SupervisorNote(Base):
    __tablename__ = 'supervisor_notes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String)
    cse_id = Column(String)
    note = Column(Text)
    created_at = Column(DateTime)
