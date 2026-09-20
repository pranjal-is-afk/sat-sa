"""
SAT-SA Supervisory Analytics Engine
Master orchestrator executing hybrid deterministic, negative-space, NLP,
and peer benchmarking analytics over canonical SOC evidence.
"""

from typing import List, Dict, Any
from datetime import datetime

from analytics.rules.critical_alert_no_escalation import evaluate_critical_alert_no_escalation
from analytics.rules.high_severity_fast_closure import evaluate_high_severity_fast_closure
from analytics.rules.alert_no_investigation import evaluate_alert_no_investigation
from analytics.rules.repeated_alerts_no_remediation import evaluate_repeated_alerts_no_remediation
from analytics.rules.repetitive_investigation_notes import evaluate_repetitive_investigations
from analytics.rules.critical_asset_missing_telemetry import evaluate_critical_asset_missing_telemetry
from analytics.rules.workflow_sequence_violations import evaluate_workflow_sequence_violations
from analytics.rules.metric_gaming_detection import evaluate_metric_gaming
from analytics.rules.peer_deviation import compute_peer_metrics, evaluate_peer_deviations
from analytics.anomaly.isolation_forest_detector import run_multivariate_anomaly_detection
from analytics.scoring.entity_risk_scorer import calculate_entity_supervisory_risk
from analytics.scoring.case_prioritizer import prioritize_findings

class SupervisoryAnalyticsEngine:
    def __init__(self, rule_version: str = "1.2.0"):
        self.rule_version = rule_version

    def run_pipeline(
        self,
        alerts: List[Dict[str, Any]],
        cases: List[Dict[str, Any]],
        assets: List[Dict[str, Any]],
        steps: List[Dict[str, Any]],
        escalations: List[Dict[str, Any]],
        remediations: List[Dict[str, Any]],
        telemetry_coverage: List[Dict[str, Any]],
        data_quality_issues: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes full analytics across all entities in the submission dataset.
        Returns:
        - raw_findings: all generated findings
        - prioritized_queue: ranked review queue
        - entity_risks: per-CSE decomposed scores
        - peer_metrics: baseline distributions
        """
        all_findings = []

        # Index data by entity and ID
        cases_map = {c["case_id"]: c for c in cases if c.get("case_id")}
        assets_map = {a["asset_id"]: a for a in assets if a.get("asset_id")}
        
        steps_by_case = {}
        for s in steps:
            cid = s.get("case_id")
            if cid:
                if cid not in steps_by_case:
                    steps_by_case[cid] = []
                steps_by_case[cid].append(s)

        # 1. Deterministic Rule R-ESC-001: Critical Alert Missing Escalation
        esc_findings = evaluate_critical_alert_no_escalation(
            alerts, escalations, assets_map, rule_version=self.rule_version
        )
        all_findings.extend(esc_findings)

        # 2. Deterministic Rule R-INV-002: High-Severity Alert Fast Closure
        fast_findings = evaluate_high_severity_fast_closure(
            alerts, cases_map, rule_version=self.rule_version
        )
        all_findings.extend(fast_findings)

        # 3. Deterministic Rule R-INV-001: Superficial Investigation
        qual_findings = evaluate_alert_no_investigation(
            alerts, cases_map, steps_by_case, rule_version=self.rule_version
        )
        all_findings.extend(qual_findings)

        # 4. Deterministic Rule R-REM-001: Repeated Alerts Without Remediation
        rem_findings = evaluate_repeated_alerts_no_remediation(
            alerts, remediations, rule_version=self.rule_version
        )
        all_findings.extend(rem_findings)

        # 5. Local NLP Rule R-INV-003: Repetitive Investigation Narratives
        nlp_findings = evaluate_repetitive_investigations(
            cases, rule_version=self.rule_version
        )
        all_findings.extend(nlp_findings)

        # 6. Negative-Space Rule R-NEG-001: Critical Asset Missing Telemetry
        neg_findings = evaluate_critical_asset_missing_telemetry(
            assets, alerts, telemetry_coverage, rule_version=self.rule_version
        )
        all_findings.extend(neg_findings)

        # 7. Workflow Sequence Violations R-SEQ-001
        seq_findings = evaluate_workflow_sequence_violations(
            cases, escalations, rule_version=self.rule_version
        )
        all_findings.extend(seq_findings)

        # 8. Metric Gaming R-GAM-001
        gam_findings = evaluate_metric_gaming(
            cases, rule_version=self.rule_version
        )
        all_findings.extend(gam_findings)

        # Group data by entity to compute entity statistics and peer baselines
        entity_ids = list(set([a.get("cse_id") for a in alerts if a.get("cse_id")] + [ass.get("cse_id") for ass in assets if ass.get("cse_id")]))
        entity_summaries = []

        for eid in entity_ids:
            ent_alerts = [a for a in alerts if a.get("cse_id") == eid]
            ent_assets = [a for a in assets if a.get("cse_id") == eid]
            ent_cases = [c for c in cases if c.get("cse_id") == eid]
            
            asset_count = max(1, len(ent_assets))
            alert_count = len(ent_alerts)
            rate = alert_count / (asset_count * 30.0) # 30 days period

            # Closures
            durations = []
            for a in ent_alerts:
                if a.get("created_at") and a.get("closed_at"):
                    try:
                        c_dt = datetime.fromisoformat(a["created_at"].rstrip("Z"))
                        cl_dt = datetime.fromisoformat(a["closed_at"].rstrip("Z"))
                        if cl_dt > c_dt:
                            durations.append((cl_dt - c_dt).total_seconds() / 60.0)
                    except Exception:
                        pass
            
            median_closure = float(sorted(durations)[len(durations)//2]) if durations else 50.0
            
            # Critical alerts vs escalations
            crit_alerts = [a for a in ent_alerts if a.get("severity") == "Critical"]
            crit_esc = [a for a in crit_alerts if a.get("escalation_id")]
            esc_rate = len(crit_esc) / max(1, len(crit_alerts))

            entity_summaries.append({
                "cse_id": eid,
                "alert_rate": rate,
                "median_closure_mins": median_closure,
                "escalation_rate": esc_rate,
                "evidence_density": sum([int(c.get("evidence_count") or 0) for c in ent_cases]) / max(1, len(ent_cases)),
                "repeat_ratio": 0.2, # Baseline
                "negative_space_ratio": len([f for f in neg_findings if f.get("entity_id") == eid]) / asset_count
            })

        # 9. Compute Sector Peer Baselines & Benchmark Rule R-BEN-001
        peer_metrics = compute_peer_metrics(entity_summaries)
        for esum in entity_summaries:
            eid = esum["cse_id"]
            ben_findings = evaluate_peer_deviations(eid, esum, peer_metrics, rule_version=self.rule_version)
            all_findings.extend(ben_findings)

        # 10. Optional Unsupervised Anomaly Detection (Isolation Forest)
        ml_findings = run_multivariate_anomaly_detection(entity_summaries)
        all_findings.extend(ml_findings)

        # 11. Calculate Decomposed Supervisory Risk Score per Entity
        entity_risks = {}
        for eid in entity_ids:
            ent_findings = [f for f in all_findings if f.get("entity_id") == eid]
            ent_dq = [q for q in (data_quality_issues or []) if q.get("record_id", "").startswith(eid)]
            risk_profile = calculate_entity_supervisory_risk(ent_findings, ent_dq)
            risk_profile["cse_id"] = eid
            risk_profile["findings_count"] = len(ent_findings)
            entity_risks[eid] = risk_profile

        # 12. Prioritize Review Queue
        prioritized_queue = prioritize_findings(all_findings)

        return {
            "findings": all_findings,
            "prioritized_queue": prioritized_queue,
            "entity_risks": entity_risks,
            "peer_metrics": peer_metrics,
            "total_findings": len(all_findings)
        }
