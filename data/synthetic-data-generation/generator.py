"""
Synthetic SOC Operational Evidence Dataset Generator for SAT-SA
Implements realistic operational profiles for 10 Critical Sector Entities (CSE-01 to CSE-10)
Injecting known ground-truth supervisory conditions for empirical validation.
"""

import os
import csv
import json
import random
from datetime import datetime, timedelta

def generate_datasets(output_dir: str = "data/sample"):
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42) # Deterministic for reproducible validation

    cses = [
        {"cse_id": "CSE-01", "name": "Northern Power Grid Corp", "sector": "Energy & Power", "criticality_tier": "Tier-1", "flaw": "HEALTHY_BASELINE"},
        {"cse_id": "CSE-02", "name": "Apex Federal Reserve Bank", "sector": "Banking & Finance", "criticality_tier": "Tier-1", "flaw": "HIGH_VOLUME_NORMAL"},
        {"cse_id": "CSE-03", "name": "National Telecom Backbone", "sector": "Telecommunications", "criticality_tier": "Tier-1", "flaw": "CRITICAL_MISSING_ESCALATION"},
        {"cse_id": "CSE-04", "name": "National Freight Rail Dispatch", "sector": "Transportation", "criticality_tier": "Tier-1", "flaw": "FAST_CLOSURES_LOW_EVIDENCE"},
        {"cse_id": "CSE-05", "name": "Strategic Defense Electronics", "sector": "Defense & Space", "criticality_tier": "Tier-1", "flaw": "BOILERPLATE_INVESTIGATIONS"},
        {"cse_id": "CSE-06", "name": "Kalpakkam Atomic Energy Station", "sector": "Nuclear Energy", "criticality_tier": "Tier-1", "flaw": "REPEATED_ALERTS_NO_REMEDIATION"},
        {"cse_id": "CSE-07", "name": "Trans-National Petroleum Pipeline", "sector": "Oil & Gas", "criticality_tier": "Tier-1", "flaw": "NEGATIVE_SPACE_SILENT_ASSETS"},
        {"cse_id": "CSE-08", "name": "Metropolitan Water Authority", "sector": "Water & Sanitation", "criticality_tier": "Tier-2", "flaw": "LOW_ACTIVITY_PEER_ANOMALY"},
        {"cse_id": "CSE-09", "name": "Regional Smart Grid Distribution", "sector": "Energy & Power", "criticality_tier": "Tier-2", "flaw": "DATA_QUALITY_ANOMALIES"},
        {"cse_id": "CSE-10", "name": "Air Cargo & Logistics Network", "sector": "Transportation", "criticality_tier": "Tier-1", "flaw": "COMPOUND_MULTI_VECTOR_GAPS"},
    ]

    base_time = datetime(2026, 8, 1, 8, 0, 0)
    period = "2026-Q3"

    all_assets = []
    all_alerts = []
    all_cases = []
    all_steps = []
    all_escalations = []
    all_remediations = []
    all_coverage = []
    ground_truth = []

    categories = ["Malware", "Identity/Credential Access", "Lateral Movement", "Data Exfiltration", "Privilege Escalation", "Reconnaissance", "Denial of Service"]
    sources = ["EDR-Falcon", "Splunk-SIEM", "PaloAlto-FW", "Azure-AD", "Suricata-NDR", "OT-Defender"]
    severities = ["Critical", "High", "Medium", "Low"]

    boilerplate_narratives = [
        "Alert inspected by shift analyst. Verified host logs and network traces. No persistence mechanisms or lateral movement observed. Host rebooted and restored to baseline operating condition. Benign event.",
        "System telemetry analyzed in accordance with standard triage checklist. Host connection tables examined. No malicious outbound traffic detected. Asset disposition marked benign and closed.",
        "Security incident reviewed. Standard antivirus definitions up to date. Hash checked against internal white-list. No indicators of compromise confirmed. Case closed with manager approval."
    ]

    for cse in cses:
        cid = cse["cse_id"]
        flaw = cse["flaw"]

        # 1. Create Assets (10-20 assets per entity)
        num_assets = 15 if cid != "CSE-02" else 30
        for i in range(1, num_assets + 1):
            aid = f"{cid}-AST-{i:03d}"
            crit = "Critical" if i <= 5 else ("High" if i <= 10 else "Medium")
            monitoring_expected = True
            
            all_assets.append({
                "asset_id": aid,
                "cse_id": cid,
                "asset_type": "SCADA Controller" if i <= 3 else ("Database Server" if i <= 6 else "Workstation"),
                "business_service": "Grid Balancing" if "Energy" in cse["sector"] else "Core Transaction Engine",
                "criticality": crit,
                "environment": "Production",
                "owner": f"Ops-Team-{i%3+1}",
                "monitoring_expected": monitoring_expected,
                "monitoring_source": "OT-Defender" if "SCADA" in aid else "EDR-Falcon"
            })

            # Coverage record
            if flaw == "NEGATIVE_SPACE_SILENT_ASSETS" and i <= 3:
                # Flawed: Silent assets, 0 observed volume despite expected monitoring
                all_coverage.append({
                    "asset_id": aid,
                    "cse_id": cid,
                    "period": period,
                    "expected_event_volume": 50000,
                    "observed_event_volume": 0,
                    "last_seen_at": (base_time - timedelta(days=25)).isoformat() + "Z",
                    "coverage_status": "Silent"
                })
                ground_truth.append({
                    "entity_id": cid,
                    "finding_type": "CRITICAL_ASSET_MISSING_TELEMETRY",
                    "rule_id": "R-NEG-001",
                    "record_id": aid,
                    "description": f"Critical asset {aid} expected to be monitored has produced zero telemetry or alerts for 25 days."
                })
            else:
                all_coverage.append({
                    "asset_id": aid,
                    "cse_id": cid,
                    "period": period,
                    "expected_event_volume": 50000,
                    "observed_event_volume": random.randint(45000, 55000),
                    "last_seen_at": (base_time + timedelta(days=29)).isoformat() + "Z",
                    "coverage_status": "Active"
                })

        # 2. Create Alerts and Cases
        num_alerts = 60 if cid != "CSE-08" else 8 # CSE-08 is abnormally low
        if cid == "CSE-02":
            num_alerts = 150 # High volume normal bank

        for a_idx in range(1, num_alerts + 1):
            aid = f"{cid}-ALT-{a_idx:04d}"
            case_id = f"{cid}-CASE-{a_idx:04d}"
            target_asset = f"{cid}-AST-{(a_idx % 5) + 1:03d}" if flaw != "NEGATIVE_SPACE_SILENT_ASSETS" else f"{cid}-AST-{(a_idx % 5) + 4:03d}"
            
            created_dt = base_time + timedelta(days=random.randint(0, 28), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            sev = "Critical" if (a_idx % 5 == 0) else ("High" if (a_idx % 3 == 0) else "Medium")
            cat = random.choice(categories)

            # Execution Gap Injections
            is_fast_closure = (flaw in ["FAST_CLOSURES_LOW_EVIDENCE", "COMPOUND_MULTI_VECTOR_GAPS"]) and (sev in ["Critical", "High"])
            is_missing_escalation = (flaw in ["CRITICAL_MISSING_ESCALATION", "COMPOUND_MULTI_VECTOR_GAPS"]) and (sev == "Critical")
            is_boilerplate = (flaw == "BOILERPLATE_INVESTIGATIONS")
            is_repeated_unremediated = (flaw == "REPEATED_ALERTS_NO_REMEDIATION") and (target_asset == f"{cid}-AST-001")
            is_data_quality_error = (flaw == "DATA_QUALITY_ANOMALIES") and (a_idx % 5 == 0)

            # Closure duration
            if is_fast_closure:
                dur_minutes = random.randint(2, 6) # < 10 mins!
            else:
                dur_minutes = random.randint(40, 120)

            closed_dt = created_dt + timedelta(minutes=dur_minutes)
            ack_dt = created_dt + timedelta(minutes=min(dur_minutes - 1, random.randint(1, 10)))

            if is_data_quality_error:
                # Invert timestamp for DQ-003 testing
                closed_dt = created_dt - timedelta(minutes=15)

            status = "Closed"
            disposition = "True Positive" if sev == "Critical" else "False Positive"

            escalation_id = None
            if not is_missing_escalation and sev == "Critical":
                escalation_id = f"{cid}-ESC-{a_idx:04d}"
                all_escalations.append({
                    "escalation_id": escalation_id,
                    "case_id": case_id,
                    "escalation_level": "Tier 3 Incident Response",
                    "escalated_to": "National CERT / Incident Commander",
                    "escalated_at": (created_dt + timedelta(minutes=20)).isoformat() + "Z",
                    "reason": f"Escalated high-impact {sev} threat on {target_asset}",
                    "acknowledged_at": (created_dt + timedelta(minutes=30)).isoformat() + "Z",
                    "resolved_at": closed_dt.isoformat() + "Z",
                    "status": "Resolved"
                })

            all_alerts.append({
                "alert_id": aid,
                "cse_id": cid,
                "created_at": created_dt.isoformat() + "Z",
                "acknowledged_at": ack_dt.isoformat() + "Z",
                "closed_at": closed_dt.isoformat() + "Z",
                "severity": sev,
                "alert_category": cat,
                "source_system": random.choice(sources),
                "asset_id": target_asset,
                "asset_criticality": "Critical" if "AST-001" in target_asset or "AST-002" in target_asset else "High",
                "status": status,
                "disposition": disposition,
                "case_id": case_id if not is_data_quality_error else f"NON_EXISTENT_CASE_{a_idx}",
                "escalation_id": escalation_id,
                "analyst_id": f"ANON-{(a_idx % 4) + 1:02d}",
                "business_service": "Grid Operation"
            })

            # Case Narrative
            if is_boilerplate:
                summary = boilerplate_narratives[0] # Exact copy-paste
            elif is_fast_closure:
                summary = "Closed per review. No action needed."
            else:
                summary = f"Investigated suspicious {cat} activity on {target_asset}. Host quarantine verified, memory strings analyzed, credentials rotated for user domain accounts. Incident mitigated cleanly."

            evidence_count = 0 if is_fast_closure else random.randint(2, 5)
            
            all_cases.append({
                "case_id": case_id,
                "cse_id": cid,
                "alert_id": aid,
                "created_at": created_dt.isoformat() + "Z",
                "investigation_started_at": ack_dt.isoformat() + "Z",
                "closed_at": closed_dt.isoformat() + "Z",
                "priority": sev,
                "investigation_summary": summary,
                "evidence_count": evidence_count,
                "closure_reason": "Resolved by Standard Triage" if not is_fast_closure else "Generic closure",
                "root_cause": f"Root vulnerability in service module on {target_asset}" if not is_fast_closure else "",
                "remediation_status": "Completed" if not is_repeated_unremediated else "None",
                "reviewer_id": "LEAD-REV-01"
            })

            # Workflow steps
            step_count = 1 if is_fast_closure else random.randint(3, 5)
            for s in range(1, step_count + 1):
                all_steps.append({
                    "step_id": f"{case_id}-STP-{s}",
                    "case_id": case_id,
                    "step_name": f"Forensic Step {s}: {['Artifact Capture', 'Memory Dump', 'Egress Inspection', 'Remediation Review'][s%4]}",
                    "step_status": "Completed",
                    "performed_by": f"ANON-{(a_idx % 4) + 1:02d}",
                    "started_at": (ack_dt + timedelta(minutes=s*5)).isoformat() + "Z",
                    "completed_at": (ack_dt + timedelta(minutes=s*8)).isoformat() + "Z",
                    "notes": f"Completed analysis for step {s}",
                    "evidence_reference": f"HASH-SHA256-{a_idx}{s}"
                })

            # Register ground-truth labels for benchmark testing
            if is_fast_closure:
                ground_truth.append({
                    "entity_id": cid,
                    "finding_type": "HIGH_SEVERITY_FAST_CLOSURE",
                    "rule_id": "R-INV-002",
                    "record_id": aid,
                    "description": f"Critical/High alert {aid} closed in {dur_minutes} mins (< peer 5th percentile) with low evidence."
                })
            if is_missing_escalation:
                ground_truth.append({
                    "entity_id": cid,
                    "finding_type": "CRITICAL_ALERT_MISSING_ESCALATION",
                    "rule_id": "R-ESC-001",
                    "record_id": aid,
                    "description": f"Critical alert {aid} on critical asset had no linked escalation."
                })
            if is_boilerplate and a_idx > 5:
                ground_truth.append({
                    "entity_id": cid,
                    "finding_type": "REPETITIVE_INVESTIGATION_NARRATIVE",
                    "rule_id": "R-INV-003",
                    "record_id": case_id,
                    "description": f"Case {case_id} investigation narrative is boilerplate copy-paste with >90% text similarity."
                })

        # Inject repeated alerts with no remediation for CSE-06
        if flaw == "REPEATED_ALERTS_NO_REMEDIATION":
            ground_truth.append({
                "entity_id": cid,
                "finding_type": "REPEATED_ALERTS_NO_REMEDIATION",
                "rule_id": "R-REM-001",
                "record_id": f"{cid}-AST-001",
                "description": f"Asset {cid}-AST-001 has >12 repeated critical/high alerts with zero root-cause remediation."
            })

    # Write CSVs
    def write_csv(filename, fieldnames, rows):
        path = os.path.join(output_dir, filename)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Generated {path} with {len(rows)} records.")

    write_csv("assets.csv", list(all_assets[0].keys()), all_assets)
    write_csv("alerts.csv", list(all_alerts[0].keys()), all_alerts)
    write_csv("cases.csv", list(all_cases[0].keys()), all_cases)
    write_csv("investigation_steps.csv", list(all_steps[0].keys()), all_steps)
    write_csv("escalations.csv", list(all_escalations[0].keys()) if all_escalations else ["escalation_id", "case_id", "escalation_level", "escalated_to", "escalated_at", "reason", "acknowledged_at", "resolved_at", "status"], all_escalations)
    write_csv("telemetry_coverage.csv", list(all_coverage[0].keys()), all_coverage)

    # Remediations (CSE-01 has active remediation, CSE-06 does not)
    sample_remediations = [
        {
            "remediation_id": "REM-001",
            "asset_id": "CSE-01-AST-001",
            "case_id": "CSE-01-CASE-0005",
            "vulnerability_or_root_cause": "Firmware buffer overflow CVE-2026-1002",
            "action_plan": "Applied vendor patch v2.4 to core grid controller",
            "status": "Completed",
            "due_date": "2026-08-15"
        }
    ]
    write_csv("remediations.csv", list(sample_remediations[0].keys()), sample_remediations)

    # Save Ground Truth for verification tests
    gt_path = os.path.join(output_dir, "ground_truth.json")
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)
    print(f"Generated ground truth file {gt_path} with {len(ground_truth)} labeled flaws.")

if __name__ == "__main__":
    generate_datasets()
