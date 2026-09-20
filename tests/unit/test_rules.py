"""
Unit Tests for Supervisory Analytics Rules
"""

import pytest
from analytics.rules.critical_alert_no_escalation import evaluate_critical_alert_no_escalation
from analytics.rules.high_severity_fast_closure import evaluate_high_severity_fast_closure
from analytics.rules.alert_no_investigation import evaluate_alert_no_investigation
from analytics.rules.repeated_alerts_no_remediation import evaluate_repeated_alerts_no_remediation
from analytics.rules.critical_asset_missing_telemetry import evaluate_critical_asset_missing_telemetry
from analytics.rules.workflow_sequence_violations import evaluate_workflow_sequence_violations

def test_critical_alert_no_escalation():
    alerts = [
        {"alert_id": "ALT-01", "cse_id": "CSE-01", "severity": "Critical", "asset_id": "AST-01", "case_id": "CASE-01"}
    ]
    assets_map = {"AST-01": {"criticality": "Critical"}}
    escalations = [] # Missing escalation

    findings = evaluate_critical_alert_no_escalation(alerts, escalations, assets_map)
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "R-ESC-001"
    assert findings[0]["severity"] == "HIGH"
    assert findings[0]["alert_id"] == "ALT-01"

def test_critical_alert_properly_escalated():
    alerts = [
        {"alert_id": "ALT-01", "cse_id": "CSE-01", "severity": "Critical", "asset_id": "AST-01", "case_id": "CASE-01"}
    ]
    assets_map = {"AST-01": {"criticality": "Critical"}}
    escalations = [{"case_id": "CASE-01", "escalation_id": "ESC-01"}]

    findings = evaluate_critical_alert_no_escalation(alerts, escalations, assets_map)
    assert len(findings) == 0

def test_high_severity_fast_closure():
    alerts = [
        {
            "alert_id": "ALT-FAST",
            "cse_id": "CSE-04",
            "severity": "Critical",
            "created_at": "2026-08-01T10:00:00Z",
            "closed_at": "2026-08-01T10:04:00Z", # 4 minutes
            "case_id": "CASE-FAST"
        }
    ]
    cases_map = {"CASE-FAST": {"evidence_count": 0}}

    findings = evaluate_high_severity_fast_closure(alerts, cases_map, fast_threshold_minutes=10.0)
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "R-INV-002"
    assert "4.0 minutes" in findings[0]["reason"]

def test_repeated_alerts_no_remediation():
    alerts = [
        {"alert_id": f"ALT-{i}", "cse_id": "CSE-06", "asset_id": "AST-TURBINE", "alert_category": "Vibration Spike"}
        for i in range(8)
    ]
    remediations = [] # No remediation record

    findings = evaluate_repeated_alerts_no_remediation(alerts, remediations, min_repeat_ratio=0.6, min_alert_count=5)
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "R-REM-001"
    assert findings[0]["asset_id"] == "AST-TURBINE"

def test_negative_space_missing_telemetry():
    assets = [
        {"asset_id": "AST-SCADA-01", "cse_id": "CSE-07", "criticality": "Critical", "monitoring_expected": True, "asset_type": "SCADA Gateway"}
    ]
    alerts = [] # No alerts
    telemetry_coverage = [
        {"asset_id": "AST-SCADA-01", "observed_event_volume": 0}
    ]

    findings = evaluate_critical_asset_missing_telemetry(assets, alerts, telemetry_coverage)
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "R-NEG-001"
    assert findings[0]["asset_id"] == "AST-SCADA-01"

def test_workflow_sequence_violation():
    cases = [
        {
            "case_id": "CASE-BAD-TIME",
            "cse_id": "CSE-09",
            "created_at": "2026-08-01T10:00:00Z",
            "investigation_started_at": "2026-08-01T10:30:00Z",
            "closed_at": "2026-08-01T10:15:00Z" # Closed before investigation started!
        }
    ]
    findings = evaluate_workflow_sequence_violations(cases, [])
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "R-SEQ-001"
