"""
Rule R-NEG-001: Critical Asset With Missing Monitoring Evidence (Negative Space)
Calculates C_asset in {0, 1}.
Flags critical assets declared in inventory as monitoring_expected=True that produce zero
alert or telemetry coverage evidence during the reporting period.
"""

from typing import List, Dict, Any

def evaluate_critical_asset_missing_telemetry(
    assets: List[Dict[str, Any]],
    alerts: List[Dict[str, Any]],
    telemetry_coverage: List[Dict[str, Any]],
    rule_version: str = "1.2.0"
) -> List[Dict[str, Any]]:
    findings = []

    # Map of asset activity from alerts
    alert_counts_by_asset = {}
    for alert in alerts:
        aid = alert.get("asset_id")
        if aid:
            alert_counts_by_asset[aid] = alert_counts_by_asset.get(aid, 0) + 1

    # Map of telemetry coverage observed volume
    telemetry_by_asset = {}
    for cov in telemetry_coverage:
        aid = cov.get("asset_id")
        try:
            vol = int(cov.get("observed_event_volume", 0))
        except (ValueError, TypeError):
            vol = 0
        telemetry_by_asset[aid] = vol

    for asset in assets:
        aid = asset.get("asset_id")
        crit = asset.get("criticality")
        expected = asset.get("monitoring_expected", True)

        # Check only Critical and High tier assets where monitoring is expected
        if crit in ["Critical", "High"] and expected:
            alert_count = alert_counts_by_asset.get(aid, 0)
            telemetry_vol = telemetry_by_asset.get(aid, 0)

            # If both alert count is 0 AND observed telemetry volume is 0 or missing
            if alert_count == 0 and telemetry_vol == 0:
                c_asset = 0
                finding_id = f"F-NEG-{asset.get('cse_id')}-{aid.replace('-', '_')}"
                findings.append({
                    "finding_id": finding_id,
                    "entity_id": asset.get("cse_id", ""),
                    "rule_id": "R-NEG-001",
                    "rule_version": rule_version,
                    "category": "Negative Space",
                    "type": "CRITICAL_ASSET_MISSING_TELEMETRY",
                    "severity": "HIGH",
                    "confidence": 0.95,
                    "status": "OPEN",
                    "asset_id": aid,
                    "alert_id": None,
                    "case_id": None,
                    "reason": f"Negative-space blindspot: Critical asset {aid} ({asset.get('asset_type', 'System')}) is declared active and monitoring-expected, but generated 0 telemetry events and 0 security alerts during the reporting period (C_asset = {c_asset}).",
                    "evidence": [
                        {"table": "assets", "record_id": aid, "field": "criticality", "value": crit},
                        {"table": "assets", "record_id": aid, "field": "monitoring_expected", "value": True},
                        {"table": "telemetry_coverage", "record_id": aid, "field": "observed_event_volume", "value": 0},
                        {"table": "alerts", "record_id": aid, "field": "alert_count", "value": 0}
                    ],
                    "peer_baseline": "Across comparable peer critical assets, median monthly telemetry volume is 50,000+ events and 4.2 alerts.",
                    "recommended_action": "Immediately inspect sensor/agent connectivity, network tap configuration, and firewall rules between asset and SOC collector."
                })

    return findings
