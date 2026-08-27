from typing import Dict, List
from sqlalchemy.orm import Session
from ..models.orm import AlertRecord, AssetRecord, CaseRecord
import numpy as np
from datetime import timedelta

def detect_negative_space(cse_id: str, batch_id: str, db: Session,
                          all_features: Dict[str, dict],
                          sector_map: Dict[str, str]) -> List[dict]:
    findings = []
    
    alerts = db.query(AlertRecord).filter(
        AlertRecord.batch_id == batch_id,
        AlertRecord.cse_id == cse_id
    ).all()
    
    assets = db.query(AssetRecord).filter(
        AssetRecord.batch_id == batch_id,
        AssetRecord.cse_id == cse_id
    ).all()
    
    cases = db.query(CaseRecord).filter(
        CaseRecord.batch_id == batch_id,
        CaseRecord.cse_id == cse_id
    ).all()
    
    alert_dates = [a.created_at for a in alerts if a.created_at]
    alert_asset_ids = set(a.asset_id for a in alerts if a.asset_id)
    
    # Type 1: MISSING_TELEMETRY — critical asset with zero alerts
    critical_assets = [a for a in assets if a.classification == 'CRITICAL']
    for asset in critical_assets:
        if asset.asset_id not in alert_asset_ids:
            # Peer context: average alerts per critical asset among peers
            peer_ratios = [
                pf.get('critical_asset_telemetry_ratio', 0)
                for pid, pf in all_features.items() if pid != cse_id
            ]
            peer_mean = float(np.mean(peer_ratios)) if peer_ratios else 0.0
            findings.append({
                'finding_type': 'MISSING_TELEMETRY',
                'asset_id': asset.asset_id,
                'description': f'Critical asset {asset.asset_id} generated ZERO security alerts in the entire submission period.',
                'expected_value': f'{peer_mean:.1f} alerts/asset/30-days (peer average)',
                'observed_value': '0 alerts',
                'severity': 'CRITICAL',
                'peer_context': {'peer_mean': peer_mean, 'peer_count': len(peer_ratios)}
            })
    
    # Type 2: MISSING_ALERT_CATEGORY — severity absent while peers have it
    this_severities = set(a.severity for a in alerts)
    sector = sector_map.get(cse_id, 'Unknown')
    peer_cse_ids = [pid for pid, sec in sector_map.items() 
                    if sec == sector and pid != cse_id]
    if not peer_cse_ids:
        peer_cse_ids = [pid for pid in all_features if pid != cse_id]
    
    for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if sev not in this_severities:
            peer_alert_counts = []
            for peer_id in peer_cse_ids:
                peer_alerts = db.query(AlertRecord).filter(
                    AlertRecord.batch_id == batch_id,
                    AlertRecord.cse_id == peer_id,
                    AlertRecord.severity == sev
                ).count()
                peer_alert_counts.append(peer_alerts)
            
            peers_with_sev = sum(1 for c in peer_alert_counts if c > 0)
            if peer_alert_counts and peers_with_sev / len(peer_alert_counts) >= 0.7:
                findings.append({
                    'finding_type': 'MISSING_ALERT_CATEGORY',
                    'asset_id': None,
                    'description': f'No {sev} severity alerts in submission. This category is present in {peers_with_sev}/{len(peer_alert_counts)} peer CSEs.',
                    'expected_value': f'{sev} alerts (present in {peers_with_sev} of {len(peer_alert_counts)} peers)',
                    'observed_value': '0 alerts',
                    'severity': 'HIGH',
                    'peer_context': {'peer_mean': float(np.mean(peer_alert_counts)) if peer_alert_counts else 0, 'peer_count': len(peer_alert_counts)}
                })
    
    # Type 3: MISSING_ESCALATION
    this_esc_rate = all_features.get(cse_id, {}).get('escalation_rate', 0.0)
    peer_esc_rates = [
        pf.get('escalation_rate', 0) 
        for pid, pf in all_features.items() if pid != cse_id
    ]
    peer_mean_esc = float(np.mean(peer_esc_rates)) if peer_esc_rates else 0.0
    if this_esc_rate < 0.08 and peer_mean_esc >= 0.15 and len(alerts) > 100:
        findings.append({
            'finding_type': 'MISSING_ESCALATION',
            'asset_id': None,
            'description': f'Severely suppressed escalation record volume: {this_esc_rate*100:.1f}% vs peer average of {peer_mean_esc*100:.1f}%. Expected escalation workflows are largely absent from submitted operational evidence.',
            'expected_value': f'{peer_mean_esc*100:.1f}% escalation rate (peer average)',
            'observed_value': f'{this_esc_rate*100:.1f}% ({int(this_esc_rate*len(cases))} of {len(cases)} cases)',
            'severity': 'HIGH',
            'peer_context': {'peer_mean': peer_mean_esc, 'peer_count': len(peer_esc_rates)}
        })
    
    return findings
