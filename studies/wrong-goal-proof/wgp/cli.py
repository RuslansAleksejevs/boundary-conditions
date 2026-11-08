"""Offline reproducibility CLI. Intentionally no live-model/API command."""

import argparse
import json
import sys
from pathlib import Path

from .adapters import TestDouble
from .analysis import analyze
from .evidence import export_evidence, verify_evidence
from .logic import SchemaError, canonical, digest
from .pipeline import audit_run, run_pipeline
from .records import (freeze, initial_requests, load_bundle, load_transcript,
                      prepare, read_json, verify_freeze, write_new)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare", help="generate disjoint CPU-checked development/holdout bundle")
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=6006)
    p = sub.add_parser("run", help="run test doubles or replay authorized recorded responses")
    p.add_argument("--bundle", required=True)
    p.add_argument("--split", choices=("dev", "holdout"), required=True)
    p.add_argument("--freeze")
    p.add_argument("--out", required=True)
    adapters = p.add_mutually_exclusive_group(required=True)
    adapters.add_argument("--double", choices=("perfect", "local-only", "abstain", "malformed"))
    adapters.add_argument("--transcript")
    p = sub.add_parser("freeze", help="apply pilot stop rule and freeze exact code/configuration")
    p.add_argument("--bundle", required=True)
    p.add_argument("--pilot", required=True)
    p.add_argument("--out", required=True)
    for name in ("audit", "analyze", "export-evidence"):
        p = sub.add_parser(name)
        p.add_argument("--bundle", required=True)
        p.add_argument("--run", required=True)
        if name != "audit":
            p.add_argument("--out", required=True)
    p = sub.add_parser("verify-evidence", help="check a standalone false-guarantee packet without a bundle")
    p.add_argument("--evidence", required=True)
    p = sub.add_parser("requests", help="export initial requests, not dependent A reviewer requests")
    p.add_argument("--bundle", required=True)
    p.add_argument("--split", choices=("dev", "holdout"), required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--freeze")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            manifest = prepare(args.out, args.seed)
            result = {"status": manifest["status"], "dataset_hash": manifest["dataset_hash"],
                      "audit": manifest["ground_truth_audit"]}
        elif args.command == "freeze":
            frozen = freeze(args.bundle, args.pilot, args.out)
            result = {"status": frozen["status"], "pilot_gate": frozen["pilot_gate"]}
        elif args.command == "verify-evidence":
            result = verify_evidence(read_json(args.evidence))
        else:
            dataset, manifest = load_bundle(args.bundle)
            if args.command == "run":
                output = Path(args.out)
                journal = output.with_suffix(output.suffix + ".events.jsonl")
                if output.exists() or journal.exists():
                    raise FileExistsError("run output exists; never overwrite a recorded run")
                adapter = TestDouble(args.double) if args.double else load_transcript(args.transcript)
                if args.split == "holdout":
                    if not args.freeze:
                        raise SchemaError("holdout requires an explicit matching freeze record")
                    verify_freeze(read_json(args.freeze), manifest, adapter)
                output.parent.mkdir(parents=True, exist_ok=True)
                with journal.open("x", encoding="utf-8") as stream:
                    def emit(event):
                        stream.write(canonical(event) + "\n")
                        stream.flush()
                    run = run_pipeline(dataset, args.split, adapter, digest(manifest), emit=emit)
                write_new(args.out, run)
                result = {"mode": run["adapter"]["kind"], "new_model_calls": 0,
                          **audit_run(dataset, run)}
            elif args.command == "requests":
                if args.split == "holdout":
                    if not args.freeze:
                        raise SchemaError("holdout request export requires a freeze")
                    frozen = read_json(args.freeze)
                    if frozen["manifest_hash"] != digest(manifest):
                        raise SchemaError("freeze/manifest mismatch")
                requests = initial_requests(dataset, args.split)
                write_new(args.out, requests)
                result = {"requests": len(requests), "new_model_calls": 0,
                          "note": "Natural reviewer prompts require translated candidates."}
            else:
                run = read_json(args.run)
                if run["manifest_hash"] != digest(manifest):
                    raise SchemaError("run/manifest mismatch")
                result = audit_run(dataset, run)
                if args.command == "analyze":
                    report = analyze(run)
                    write_new(args.out, report)
                    result = {"mode": report["mode"], "split": report["split"],
                              "new_model_calls": report["new_model_calls"],
                              "primary": report["primary_fault_S_minus_B"]}
                elif args.command == "export-evidence":
                    packet = export_evidence(dataset, run)
                    write_new(args.out, packet)
                    result = verify_evidence(packet)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (SchemaError, ValueError, OSError, KeyError, TypeError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
