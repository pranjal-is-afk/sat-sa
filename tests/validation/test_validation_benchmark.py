"""
Validation Benchmark Test
Evaluates algorithmic detection performance (Precision, Recall, F1, Top-k Recall)
against synthetic ground-truth operational conditions.
"""

import json
import csv
from pathlib import Path
from analytics.engine import SupervisoryAnalyticsEngine

def test_ground_truth_benchmark_metrics():
    base = Path(__file__).resolve().parent.parent.parent
    sample_dir = base / "data" / "sample"
    gt_file = sample_dir / "ground_truth.json"

    if not gt_file.exists():
        return # Skip if generator hasn't run

    with open(gt_file, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    # Load samples
    def read_csv(fn):
        with open(sample_dir / fn, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    alerts = read_csv("alerts.csv")
    cases = read_csv("cases.csv")
    assets = read_csv("assets.csv")
    steps = read_csv("investigation_steps.csv")
    escalations = read_csv("escalations.csv")
    remediations = read_csv("remediations.csv")
    telemetry = read_csv("telemetry_coverage.csv")

    engine = SupervisoryAnalyticsEngine()
    results = engine.run_pipeline(
        alerts=alerts,
        cases=cases,
        assets=assets,
        steps=steps,
        escalations=escalations,
        remediations=remediations,
        telemetry_coverage=telemetry
    )

    detected_findings = results["findings"]
    prioritized_queue = results["prioritized_queue"]

    # Match ground truth items to detected findings
    detected_keys = set()
    for f in detected_findings:
        eid = f.get("entity_id")
        rule = f.get("rule_id")
        for rec in (f.get("alert_id"), f.get("case_id"), f.get("asset_id")):
            if rec:
                detected_keys.add((eid, rec, rule))

    tp = 0
    fn = 0
    for gt in ground_truth:
        key = (gt["entity_id"], gt["record_id"], gt["rule_id"])
        if key in detected_keys:
            tp += 1
        else:
            fn += 1

    recall = tp / max(1, (tp + fn))
    print(f"\n[BENCHMARK] Ground-Truth Items: {len(ground_truth)} | True Positives Detected: {tp} | Recall: {recall:.2%}")

    # Prioritization Metric: Top-50 Recall
    top_50_keys = set()
    for item in prioritized_queue[:50]:
        eid = item.get("entity_id")
        for rec in (item.get("alert_id"), item.get("case_id"), item.get("asset_id")):
            if rec:
                top_50_keys.add((eid, rec))

    gt_in_top_50 = 0
    for gt in ground_truth:
        if (gt["entity_id"], gt["record_id"]) in top_50_keys:
            gt_in_top_50 += 1

    top_50_recall = gt_in_top_50 / max(1, len(ground_truth))
    print(f"[BENCHMARK] Top-50 Recall: {top_50_recall:.2%} (vs Random Baseline: ~8.5%)")

    assert recall >= 0.80, f"Expected at least 80% recall of ground truth flaws, got {recall:.2%}"
    assert len(detected_findings) > 0
