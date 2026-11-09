"""Publish and check a development-only view without releasing held-out tasks.

Export requires the unchanged complete private campaign to pass its full audit.
Public verification rechecks hashes, pilot mathematics and aggregate analysis;
it does NOT reproduce full acquisition or cross-split checks without that corpus.
No provider or credential access is performed.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from export_campaign import privacy_check
from wgp.analysis import analyze
from wgp.live import (analyze_live, audit_campaign, audit_live, live_pilot_gate,
                      load_live, read_json, validate_go)
from wgp.live_evidence import export_live_evidence, verify_live_evidence
from wgp.live_http import interpret_receipt
from wgp.logic import canonical, digest, keys
from wgp.pipeline import audit_content, timestamp
from wgp.records import write_new


KIND = "development_only_public_view_not_full_campaign"
JSON_FILES = ("development-cases.json", "manifest.json", "freeze.json", "run.json",
              "analysis.json", "evidence.json", "audit.json", "gate.json")
FILES = (*JSON_FILES, "budget.jsonl")


def validate_subset(subset):
    keys(subset, ("version", "kind", "source_dataset_hash", "cases"))
    if (subset["version"] != 1 or subset["kind"] != "development_subset_not_full_dataset"
            or type(subset["cases"]) is not list or len(subset["cases"]) != 20):
        raise ValueError("not a twenty-original development subset")
    cases = subset["cases"]
    if any(case["split"] != "dev" or not case["id"].startswith("dev-") for case in cases):
        raise ValueError("held-out or foreign case in development-only view")
    if (len({case["id"] for case in cases}) != 20
            or Counter(case["group"] for case in cases) != {"natural": 8, "fault": 8, "equivalent": 4}):
        raise ValueError("development case IDs or populations changed")
    return cases


def inventory(path):
    result = {}
    for name in FILES:
        data = (path / name).read_bytes()
        result[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        if name in JSON_FILES:
            result[name]["canonical_digest"] = digest(read_json(path / name))
    return result


def verify_pilot(path):
    path = Path(path)
    record = read_json(path / "EXPORT.json")
    if (record["kind"] != KIND or set(record["files"]) != set(FILES)
            or record["files"] != inventory(path)):
        raise ValueError("pilot-view inventory mismatch")
    if (path / "dataset.json").exists() or (path / "main").exists():
        raise ValueError("this view must not contain the full dataset or main stage")
    values = {name: read_json(path / name) for name in JSON_FILES}
    for value in values.values():
        privacy_check(value)
    subset, run, manifest = (values[name] for name in
                            ("development-cases.json", "run.json", "manifest.json"))
    cases = validate_subset(subset)
    if (run["split"] != "dev" or run["stage"] != "pilot-v1"
            or run["adapter"]["kind"] != "live_model_acquisition"
            or run["dataset_hash"] != subset["source_dataset_hash"]
            or run["dataset_hash"] != manifest["dataset_hash"]
            or run["manifest_hash"] != digest(manifest)):
        raise ValueError("pilot-view source binding mismatch")
    validate_go(run["go"], manifest, "pilot-v1")
    math = audit_content({"splits": {"dev": cases}}, run, live=True)
    calculated = analyze(run)
    saved = values["analysis.json"]
    # The shared mathematical analyzer describes scheduled logical roles. Live
    # accounting instead sums physical receipts (including technical retries and
    # excluding blocked, unsent dependent roles). Recompute that distinction.
    physical = [interpret_receipt(receipt, manifest["configuration"]) for receipt in run["receipts"]]
    calculated["usage"] = {}
    for field in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens", "cost_usd"):
        known = [receipt["usage"][field] for receipt in physical if receipt["usage"][field] is not None]
        calculated["usage"][field] = {"known_sum": sum(known), "known_attempts": len(known),
                                     "physical_attempts": len(physical),
                                     "total": sum(known) if len(known) == len(physical) else None}
    calculated["local_adapter_latency_seconds"] = sum(receipt["latency_seconds"] for receipt in run["receipts"])
    prose_only = {"latency_note", "interpretation"}
    if any(canonical(saved[key]) != canonical(value) for key, value in calculated.items() if key not in prose_only):
        raise ValueError("saved aggregate analysis differs from recomputed pilot outcomes")
    if (saved["source_run_hash"] != digest(run) or saved["manifest_hash"] != digest(manifest)
            or saved["dataset_hash"] != subset["source_dataset_hash"]):
        raise ValueError("analysis binding mismatch")
    evidence = values["evidence.json"]
    evidence_check = verify_live_evidence(evidence)
    if (evidence["source_run_hash"] != digest(run)
            or evidence["manifest_hash"] != digest(manifest)
            or evidence["dataset_hash"] != subset["source_dataset_hash"]
            or sum(len(case["answers"]) for case in evidence["cases"]) != math["confirmed_false_guarantees"]):
        raise ValueError("false-guarantee evidence binding/count mismatch")
    raw = (path / "budget.jsonl").read_text(encoding="utf-8")
    if not raw.endswith("\n") or [json.loads(line) for line in raw.splitlines()] != run["ledger_events"]:
        raise ValueError("pilot wallet is not the exact saved run ledger")
    frozen = values["freeze.json"]
    if (frozen["pilot_run_hash"] != digest(run) or frozen["manifest_hash"] != digest(manifest)
            or frozen["pilot_gate"] != values["gate.json"]):
        raise ValueError("prospective freeze binding mismatch")
    return {"valid": True, "kind": KIND, "originals": len(cases), **math,
            "evidence": evidence_check, "aggregate_analysis_recomputed": True,
            "new_model_calls": 0, "full_acquisition_audit_reproduced": False,
            "dev_holdout_separation_reproduced": False, "provenance_authenticated": False}


def export_pilot(source, target):
    source, target = Path(source), Path(target)
    # A stopped permission review creates no main directory. Refuse an ongoing,
    # crashed or completed main here; complete campaigns have a separate export.
    if (source / "main").exists():
        raise ValueError("pilot-only export requires an unstarted main stage")
    source_audit = audit_campaign(source)
    if set(source_audit["stages"]) != {"pilot-v1"}:
        raise ValueError("this pilot-only export is limited to the original pilot")
    dataset, manifest = load_live(source, check_code=True)
    run = read_json(source / "pilot-v1" / "run.json")
    files = {
        "development-cases.json": {"version": 1, "kind": "development_subset_not_full_dataset",
                                   "source_dataset_hash": digest(dataset), "cases": dataset["splits"]["dev"]},
        "manifest.json": manifest, "freeze.json": read_json(source / "freeze.json"), "run.json": run,
        "analysis.json": analyze_live(dataset, manifest, run),
        "evidence.json": export_live_evidence(dataset, manifest, run),
        "audit.json": audit_live(dataset, manifest, run),
        "gate.json": live_pilot_gate(dataset, manifest, run),
    }
    validate_subset(files["development-cases.json"])
    ledger = (source / "budget.jsonl").read_text(encoding="utf-8")
    for value in files.values():
        privacy_check(value)
    for line in ledger.splitlines():
        privacy_check(json.loads(line))
    target.mkdir(parents=True, exist_ok=False)
    for name, value in files.items():
        write_new(target / name, value)
    with (target / "budget.jsonl").open("x", encoding="utf-8") as stream:
        stream.write(ledger)
    record = {
        "version": 1, "kind": KIND, "exported_at": timestamp(),
        "full_private_campaign_audit_passed_before_export": True,
        "full_private_campaign_audit_hash": digest(source_audit),
        "source_run_hash": digest(run), "source_manifest_hash": digest(manifest),
        "held_out_task_records_released": 0, "new_calls_sent_by_export": 0,
        "original_actual_model_calls": run["new_model_calls"],
        "raw_event_journals_exported": False, "private_account_records_exported": False,
        "provenance_authenticated": False,
        "scope": "Exact pilot records and a labeled development subset, not the complete campaign dataset. Public checks repeat pilot mathematics and aggregate analysis, not full acquisition or cross-split exclusion auditing. Manifest/freeze preserve hashes and schedule metadata only for the withheld holdout.",
        "privacy_review": "Automated known-pattern scan passed; manual review remains required. The source scientific pilot authorization reference is preserved unchanged, not replaced by private coordination messages.",
        "files": inventory(target),
    }
    privacy_check(record)
    write_new(target / "EXPORT.json", record)
    return verify_pilot(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export")
    export.add_argument("--campaign", type=Path, required=True)
    export.add_argument("--out", type=Path, required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--view", type=Path, required=True)
    args = parser.parse_args()
    result = (export_pilot(args.campaign, args.out) if args.command == "export"
              else verify_pilot(args.view))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()