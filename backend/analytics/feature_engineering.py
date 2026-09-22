import json
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.orm import AlertRecord, CaseRecord, AssetRecord

def compute_features(cse_id: str, batch_id: str, db: Session) -> dict:
    """Compute 11-feature vector for a CSE from its records."""
    
    alerts = db.query(AlertRecord).filter(
        AlertRecord.batch_id == batch_id,
        AlertRecord.cse_id == cse_id
    ).all()
    
    cases = db.query(CaseRecord).filter(
        CaseRecord.batch_id == batch_id,
        CaseRecord.cse_id == cse_id
    ).all()
    
    assets = db.query(AssetRecord).filter(
        AssetRecord.batch_id == batch_id,
        AssetRecord.cse_id == cse_id
    ).all()
    
    critical_alerts = [a for a in alerts if a.severity == 'CRITICAL']
    
    # Feature 1: critical_fast_closure_rate
    fast_closed = [a for a in critical_alerts 
                   if a.closure_minutes is not None and a.closure_minutes < 8]
    critical_fast_closure_rate = len(fast_closed) / len(critical_alerts) if critical_alerts else 0.0
    
    # Feature 2: escalation_rate
    escalated_cases = [c for c in cases if c.escalated is True]
    escalation_rate = len(escalated_cases) / len(cases) if cases else 0.0
    
    # Feature 3: mean_closure_time_critical
    closure_times = [a.closure_minutes for a in critical_alerts 
                     if a.closure_minutes is not None]
    mean_closure_time_critical = float(np.mean(closure_times)) if closure_times else 0.0
    
    # Feature 4: investigation_text_similarity (filled by text_similarity.py)
    investigation_text_similarity = 0.0
    
    # Feature 5: case_linkage_rate
    linked = [a for a in critical_alerts if a.case_id is not None]
    case_linkage_rate = len(linked) / len(critical_alerts) if critical_alerts else 1.0
    
    # Feature 6: alert_category_coverage
    severity_levels = set(a.severity for a in alerts)
    alert_category_coverage = float(len(severity_levels))
    
    # Feature 7: critical_asset_telemetry_ratio
    critical_assets = [a for a in assets if a.classification == 'CRITICAL']
    if critical_assets:
        # Get date range from alerts
        dates = [a.created_at for a in alerts if a.created_at is not None]
        if dates:
            span_days = max((max(dates) - min(dates)).days, 1)
        else:
            span_days = 90
        critical_asset_ids = set(ca.asset_id for ca in critical_assets)
        alerts_from_critical = [a for a in alerts if a.asset_id in critical_asset_ids]
        ratio = (len(alerts_from_critical) / len(critical_assets)) * (30 / span_days)
        critical_asset_telemetry_ratio = float(ratio)
    else:
        critical_asset_telemetry_ratio = float(len(alerts)) / 30.0  # fallback
    
    # Feature 8: low_activity_window_count
    dates = [a.created_at for a in alerts if a.created_at is not None]
    low_activity_window_count = 0.0
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        span_days = max((max_date - min_date).days, 7)
        num_weeks = max(span_days // 7, 1)
        mean_weekly = len(alerts) / num_weeks
        for i in range(num_weeks):
            window_start = min_date + timedelta(days=i*7)
            window_end = window_start + timedelta(days=7)
            window_count = sum(1 for d in dates if window_start <= d < window_end)
            if window_count < 0.05 * mean_weekly:
                low_activity_window_count += 1
    
    # Feature 9: closure_time_cv
    if len(closure_times) >= 2:
        cv = float(np.std(closure_times) / np.mean(closure_times)) if np.mean(closure_times) > 0 else 0.0
        closure_time_cv = cv
    else:
        closure_time_cv = 1.0  # neutral (no data = not suspicious)
    
    # Features 10-11: peer ranks — placeholders filled by statistical.py
    peer_escalation_percentile = 50.0
    peer_closure_time_percentile = 50.0
    
    return {
        'critical_fast_closure_rate': critical_fast_closure_rate,
        'escalation_rate': escalation_rate,
        'mean_closure_time_critical': mean_closure_time_critical,
        'investigation_text_similarity': investigation_text_similarity,
        'case_linkage_rate': case_linkage_rate,
        'alert_category_coverage': alert_category_coverage,
        'critical_asset_telemetry_ratio': critical_asset_telemetry_ratio,
        'low_activity_window_count': low_activity_window_count,
        'closure_time_cv': closure_time_cv,
        'peer_escalation_percentile': peer_escalation_percentile,
        'peer_closure_time_percentile': peer_closure_time_percentile,
    }
