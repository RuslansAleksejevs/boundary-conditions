#!/usr/bin/env python3
"""Minimized public export of audited real runs; never contacts a model.

This reporting helper is separate from the frozen acquisition/analysis modules.
It does not change outcomes or release financial reservations. Source logs stay
private. Output must be a new directory so prior exports cannot be overwritten.
"""

import argparse
from collections import Counter
from datetime import datetime
from decimal import Decimal
import hashlib
from html import escape
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sl.analysis import analyze
from sl.continuation import effective_pilot_sources
from sl.environment import strict_json
from sl.protocol import canonical, digest


def load_run(path, phase):
    manifest = strict_json((path / "manifest.json").read_text(encoding="utf-8"))
    run = strict_json((path / "run.json").read_text(encoding="utf-8"))
    if manifest["phase"] != phase or manifest["acquisition_mode"] != "official_https":
        raise ValueError("report export requires the specified real acquisition phase")
    return manifest, run, analyze(manifest, run)


def stage_cost(manifest, run, report, reconciled=None):
    calls = run["calls"]
    known = sum((Decimal(str(c["cost_usd"])) for c in calls if c["cost_usd"] is not None), Decimal(0))
    unknown = sum(c["cost_usd"] is None for c in calls)
    if reconciled is not None and (not unknown or reconciled < known):
        raise ValueError("reconciliation must cover an unresolved stage without reducing known cost")
    wall = None
    if calls:
        start = min(datetime.fromisoformat(c["acquisition"]["started_at_utc"]) for c in calls)
        end = max(datetime.fromisoformat(c["acquisition"]["finished_at_utc"]) for c in calls)
        wall = (end - start).total_seconds()
    return {
        "phase": manifest["phase"], "seed": manifest["seed"],
        "manifest_hash": manifest["manifest_hash"], "run_hash": digest(run),
        "code_revision": manifest["code_revision"],
        "planned_requests": manifest["planned_requests"], "actual_requests": len(calls),
        "retries": run["retries_used"], "stop_reason": run["stop_reason"],
        "statuses": dict(Counter(c["status"] for c in calls)),
        "accepted_receipt_cost_usd": str(known), "unknown_receipt_cost_calls": unknown,
        "separately_reconciled_stage_cost_usd": None if reconciled is None else str(reconciled),
        "billing_evidence": "Provider receipts; separately reconciled amount, if present, is coordinator-reported read-only account verification.",
        "latency_seconds": sum(c["latency_seconds"] for c in calls), "wall_seconds": wall,
        "token_usage": report["cost"]["token_usage"],
        "cumulative_charged_or_reserved_usd": report["audit"]["charged_or_reserved_campaign_usd"],
        "pilot_gate": report["pilot_gate"],
    }


def selected_traces(manifest, run):
    scenarios = {s["scenario_id"]: s for s in manifest["scenarios"]}
    summaries = {s["scenario_id"]: s for s in run["summaries"]}
    chosen = set()
    for family in sorted({s["family"] for s in scenarios.values() if s["attacked"]}):
        chosen.add(min(sid for sid, s in scenarios.items() if s["attacked"] and s["family"] == family))
    effects = sorted(r["scenario_id"] for r in run["rows"]
                     if r["attacked"] and r["condition"] == "S-P" and r["score"] and r["score"]["effect"])
    if effects:
        chosen.add(effects[0])
    call_map = {}
    for call in run["calls"]:
        call_map[call["call_id"]] = call
    result = []
    for sid in sorted(chosen):
        rows = [r for r in run["rows"] if r["scenario_id"] == sid]
        result.append({
            "scenario": scenarios[sid], "summary": summaries[sid],
            "conditions": [{"condition": r["condition"], "status": r["status"],
                            "score": r["score"], "gate_replay": r["gate_replay"],
                            "visible_response": call_map.get(sid + "/" + r["condition"], {}).get("text")}
                           for r in rows],
        })
    return result


def paired_svg(primary, pilot_only=False):
    """A point/interval plot of the two frozen primary contrasts, in pp."""
    width, height = 900, 270
    left, right, top = 290, 850, 80
    x = lambda value: left + (value + 100) * (right - left) / 200
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<g font-family="Arial, sans-serif" fill="#17223b">',
             '<text x="24" y="28" font-size="19">' + ("Development pilot only: " if pilot_only else "") + 'paired forbidden-effect differences</text>']
    for tick in (-100, -50, 0, 50, 100):
        lines += [f'<line x1="{x(tick):.2f}" y1="48" x2="{x(tick):.2f}" y2="184" stroke="#d1d5db"/>',
                  f'<text x="{x(tick):.2f}" y="205" font-size="12" text-anchor="middle">{tick:+d}</text>']
    names = {("S-P", "S-D"): "Source label: S-P − S-D", ("S-P", "E-P"): "Transformation: S-P − E-P"}
    for index, row in enumerate(primary):
        y = top + index * 74
        label = names[(row["a"], row["b"])]
        lines.append(f'<text x="24" y="{y+5}" font-size="15">{escape(label)}</text>')
        if "complete_pairs" in row:
            lines.append(f'<text x="24" y="{y+24}" font-size="12">{row["complete_pairs"]}/{row["scheduled_pairs"]} complete/scheduled pairs</text>')
        if row["difference_pp"] is None:
            lines.append(f'<text x="{x(0):.2f}" y="{y+5}" text-anchor="middle">No complete pairs</text>')
            continue
        for key, color, dy, stroke in (("bounded_independent_cluster_95_ci_pp", "#8ca6c4", 7, 5),
                                       ("cluster_bootstrap_95_ci_pp", "#183e70", 0, 3)):
            interval = row[key]
            if interval is not None:
                lines.append(f'<line x1="{x(interval[0]):.2f}" y1="{y+dy}" x2="{x(interval[1]):.2f}" y2="{y+dy}" stroke="{color}" stroke-width="{stroke}"/>')
        lines.append(f'<circle cx="{x(row["difference_pp"]):.2f}" cy="{y}" r="5" fill="#183e70"/>')
    lines += ['<text x="570" y="228" text-anchor="middle" font-size="13">Difference in percentage points (positive = more forbidden effects in S-P)</text>',
              '<text x="24" y="254" font-size="12">Dark: 95% paired cluster bootstrap. Light: conservative bounded-cluster interval. Shared templates limit generalization.</text>',
              '</g></svg>']
    return "\n".join(lines) + "\n"


def fmt(value, digits=2):
    return "unknown" if value is None else f"{value:.{digits}f}"


def markdown_results(report, campaign):
    pilot_only = campaign["acquisition_scope"] == "development_pilot_only"
    pilot_passed = pilot_only and report["pilot_gate"].get("passed") is True
    title = ("Real pilot — gate " + ("passed" if pilot_passed else "failed") + "; main not included") if pilot_only else "Real-model results"
    lines = ["# " + title, "",
             "One fixed hosted Qwen3.5-122B-A10B / Alibaba configuration. " +
             (("The pilot gate passed. " if pilot_passed else "The pilot gate failed. ") +
              "No main acquisition is included in this export. These observations are development data, not held-out evidence."
              if pilot_only else "Main observations are not pooled with development pilots."), "",
             "## " + ("Repair-pilot" if pilot_only else "Main") + " condition table", "",
             "Effects are actual protected false-to-true events; attempts are separate. "
             "Invalid action batches execute nothing but are not valid safe completions.", "",
             "| Population | Condition | Effects | Attempts | Correct | Safe + correct | Valid | Missing |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in report["condition_table"]:
        metrics = row["metrics"]
        cells = [f'{metrics[key]["events"]}/{metrics[key]["observed"]}'
                 for key in ("effect", "attempt", "task_correct", "safe_and_correct")]
        lines.append("| " + " | ".join(["attacked" if row["attacked"] else "clean", row["condition"], *cells,
                                          str(row["valid_responses"]), str(row["scheduled"]-metrics["effect"]["observed"])]) + " |")
    lines += ["", "## " + ("Descriptive pilot calculations for planned primary contrasts" if pilot_only else "Primary paired contrasts"), "",
              "| Contrast | Complete / scheduled | Difference (pp) | Bootstrap 95% CI | Bounded-cluster 95% CI | Scheduled bounds | Holm p |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    interval = lambda values: "unknown" if values is None else "[" + ", ".join(fmt(v) for v in values) + "]"
    for row in report["primary"]:
        lines.append(f'| {row["a"]} − {row["b"]} | {row["complete_pairs"]}/{row["scheduled_pairs"]} | {fmt(row["difference_pp"])} | '
                     f'{interval(row["cluster_bootstrap_95_ci_pp"])} | {interval(row["bounded_independent_cluster_95_ci_pp"])} | '
                     f'{interval(row["scheduled_difference_bounds_pp"])} | {fmt(row.get("holm_two_primary_p"), 4)} |')
    length = report["length_matching"]
    lines += ["", "![Paired differences with two uncertainty intervals](primary-effects.svg)", "",
              "A degenerate bootstrap interval does not establish equivalence. The conservative "
              "interval also assumes independent scenario clusters; shared templates remain a limitation.", "",
              "## Length matching", "",
              f'Unmatched: {length["unmatched"]}/{length["assessable"]} assessable attacked summaries. '
              f'Predeclared inadequate-control flag: `{length["too_many_unmatched"]}`. '
              "The summary-versus-extract comparison measures a transformation bundle, not pure paraphrasing. "
              "Summary-dependent matched subsets are descriptive.", "",
              "## Acquisition and spending", "",
              "| Stage | Actual / planned calls | Technical retries | Accepted receipt cost (USD) | Separately reconciled total (USD) | Summed latency (s) |",
              "| --- | --- | --- | --- | --- | --- |"]
    for stage in campaign["stages"]:
        lines.append(f'| {stage["phase"]} | {stage["actual_requests"]}/{stage["planned_requests"]} | {stage["retries"]} | '
                     f'{stage["accepted_receipt_cost_usd"]} | {stage["separately_reconciled_stage_cost_usd"] or "—"} | {stage["latency_seconds"]:.3f} |')
    lines += ["", f'Total actual API requests: {campaign["total_actual_requests"]}. '
              f'Accounted billed cost: USD {campaign["accounted_billed_cost_usd"]}. '
              f'Additional unresolved-cost calls: {campaign["additional_unresolved_cost_calls"]}. '
              f'Final conservative wallet charge/reservation: USD {campaign["charged_or_reserved_usd"]}. '
              "The wallet retains full reserves for rejected receipts and unbilled/unresolved HTTP errors.", "",
              "## Scope and files", "",
              "`analysis.json` contains every predeclared calculation: intervals, defense comparisons, family breakdowns, "
              "missingness bound and utility result. `manifest.json`, `outcomes.json`, `summaries.json`, "
              "`calls.json` and `traces.json` contain reviewed synthetic data and minimized records. "
              "Private credentials, authorization records, provider generation identifiers and hidden "
              "reasoning are not published. Hashes establish internal reproducibility, not an independently "
              "signed provider attestation. Hard-allowlist replay is an engineering control, not an "
              "interactive model defense or a new model experiment.", ""]
    return "\n".join(lines)


def export(main_path, pilot_path, failed_path, reconciled, out):
    pilot_m, pilot_r, pilot_report = load_run(pilot_path, "pilot_repair")
    failed_m, failed_r, failed_report = load_run(failed_path, "pilot")
    if pilot_m["pilot_binding"]["run_hash"] != digest(failed_r):
        raise ValueError("repair/failed-pilot binding mismatch")
    chain = [(failed_r, pilot_r)]
    stages = [stage_cost(failed_m, failed_r, failed_report, reconciled), stage_cost(pilot_m, pilot_r, pilot_report)]
    if main_path is not None:
        main_m, main_r, report = load_run(main_path, "main")
        if not pilot_report["pilot_gate"]["passed"]:
            raise ValueError("main report requires the passing pilot used at freeze")
        binding = main_m["pilot_binding"]
        if binding["manifest_hash"] != pilot_m["manifest_hash"] or binding["run_hash"] != digest(pilot_r):
            raise ValueError("main/pilot binding mismatch")
        if main_m["code_hashes"] != effective_pilot_sources(pilot_m, pilot_r) or main_m["config"] != pilot_m["config"]:
            raise ValueError("main acquisition changed after its passing pilot")
        chain.append((pilot_r, main_r))
        stages.append(stage_cost(main_m, main_r, report))
    else:
        main_m, main_r, report = pilot_m, pilot_r, pilot_report
    for earlier, later in chain:
        if earlier["ledger"] != later["ledger"][:len(earlier["ledger"])]:
            raise ValueError("campaign financial chain mismatch")
    accounted = sum((Decimal(s["separately_reconciled_stage_cost_usd"] or s["accepted_receipt_cost_usd"]) for s in stages), Decimal(0))
    unresolved = sum(s["unknown_receipt_cost_calls"] for s in stages if s["separately_reconciled_stage_cost_usd"] is None)
    campaign = {"stages": stages, "total_actual_requests": sum(s["actual_requests"] for s in stages),
                "accounted_billed_cost_usd": str(accounted), "additional_unresolved_cost_calls": unresolved,
                "charged_or_reserved_usd": stages[-1]["cumulative_charged_or_reserved_usd"],
                "exporter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "acquisition_scope": "development_pilot_only" if main_path is None else "held_out_main",
                "evidence_label": "REAL_MODEL_OBSERVATIONS", "export_schema_version": 2}
    if "continuation" in pilot_r:
        parent = pilot_r["continuation"]["parent_run"]
        new_calls = pilot_r["calls"][len(parent["calls"]):]
        campaign["pilot_operational_segments"] = {
            "note": "The composite pilot is counted once above; these segment counts are not additional calls.",
            "original_interrupted_attempts": len(parent["calls"]),
            "continuation_new_attempts": len(new_calls),
            "original_gate": pilot_r["continuation"]["plan"]["original_gate"],
            "amended_composite_gate": pilot_report["pilot_gate"],
            "continuation_plan_hash": pilot_r["continuation"]["plan"]["plan_hash"],
            "original_run_hash": digest(parent),
        }
    call_fields = ("call_id", "attempt", "status", "usage", "cost_usd", "model_version", "latency_seconds",
                   "retryable", "request_hash", "wire_hash", "text")
    objects = {"manifest.json": main_m, "analysis.json": report, "campaign.json": campaign,
               "outcomes.json": main_r["rows"], "summaries.json": main_r["summaries"],
               "calls.json": [{k: c[k] for k in call_fields} for c in main_r["calls"]],
               "traces.json": selected_traces(main_m, main_r),
               "pilot-analysis.json": pilot_report, "failed-pilot-analysis.json": failed_report}
    # This is a conservative last check, not a substitute for manual publication review.
    payload = canonical(objects)
    for forbidden in ("/Users/", "happy-file://", "authorization_reference", "OPENROUTER_API_KEY", "sk-or-v1-"):
        if forbidden in payload:
            raise ValueError("private material detected in candidate public export")
    out.mkdir(parents=True, exist_ok=False)
    for name, value in objects.items():
        (out / name).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (out / "primary-effects.svg").write_text(paired_svg(report["primary"], pilot_only=main_path is None), encoding="utf-8")
    (out / "RESULTS.md").write_text(markdown_results(report, campaign), encoding="utf-8")
    return {"reported_manifest_hash": main_m["manifest_hash"], "actual_requests": campaign["total_actual_requests"],
            "acquisition_scope": campaign["acquisition_scope"],
            "accounted_billed_cost_usd": campaign["accounted_billed_cost_usd"], "new_model_requests": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", type=Path, help="omit for an explicitly labeled pilot-only report")
    for name in ("pilot", "failed-pilot", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--reconciled-failed-cost-usd", type=Decimal, required=True,
                        help="read-only account-confirmed first-pilot total; never changes the wallet")
    args = parser.parse_args()
    if not args.reconciled_failed_cost_usd.is_finite() or args.reconciled_failed_cost_usd < 0:
        parser.error("reconciled cost must be finite and nonnegative")
    print(canonical(export(args.main, args.pilot, args.failed_pilot, args.reconciled_failed_cost_usd, args.out)))


if __name__ == "__main__":
    main()