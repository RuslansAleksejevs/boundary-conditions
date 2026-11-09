"""Explicit live commands. Preparation/audit never read a credential or send HTTP."""

import argparse
import json
import os
import sys
from pathlib import Path

from .live import (analyze_live, audit_campaign, audit_live, freeze_live,
                   known_transport_fixture_datasets, live_pilot_gate, load_live,
                   prepare_live, read_json as read_live_json, revised_pilot_manifest, run_live_stage, validate_go)
from .live_evidence import export_live_evidence, verify_live_evidence
from .logic import SchemaError, digest
from .records import read_json, write_new


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare", help="prepare one fresh campaign, with every inspected test bundle excluded")
    p.add_argument("--campaign", required=True)
    p.add_argument("--configuration", required=True)
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--exclude-dataset", action="append", default=[])
    p = sub.add_parser("preflight", help="CPU-only check of exact source, manifest and supplied coordinator GO")
    p.add_argument("--campaign", required=True)
    p.add_argument("--go", required=True)
    p.add_argument("--stage", choices=("pilot-v1", "pilot-v2", "main"), required=True)
    p = sub.add_parser("acquire", help="the only command that can send model requests; explicit coordinator GO required")
    p.add_argument("--campaign", required=True)
    p.add_argument("--go", required=True)
    p.add_argument("--stage", choices=("pilot-v1", "pilot-v2", "main"), required=True)
    p = sub.add_parser("revise-interface", help="record one transport-only correction after a failed real pilot")
    p.add_argument("--campaign", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--authorization-reference", required=True)
    p = sub.add_parser("freeze", help="freeze a passing real pilot; refuses fixtures")
    p.add_argument("--campaign", required=True)
    p.add_argument("--pilot-stage", choices=("pilot-v1", "pilot-v2"), default="pilot-v1")
    p = sub.add_parser("audit-campaign", help="verify all stages and the entire shared wallet prefix")
    p.add_argument("--campaign", required=True)
    for command in ("audit", "pilot-gate", "analyze", "export-evidence"):
        p = sub.add_parser(command)
        p.add_argument("--campaign", required=True)
        p.add_argument("--stage", choices=("pilot-v1", "pilot-v2", "main"), required=True)
        if command in ("analyze", "export-evidence"):
            p.add_argument("--out", required=True)
    p = sub.add_parser("verify-evidence", help="verify actual visible answers and exact mathematical counterexamples")
    p.add_argument("--evidence", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            extra = known_transport_fixture_datasets() + [read_json(p) for p in args.exclude_dataset]
            manifest = prepare_live(args.campaign, read_json(args.configuration), args.seed, extra)
            result = {"manifest_hash": digest(manifest), "configuration_hash": manifest["configuration_hash"],
                      "code_hashes_hash": digest(manifest["code_hashes"]),
                      "ground_truth_audit": manifest["ground_truth_audit"], "model_calls": 0,
                      "status": "prepared; coordinator preflight and authorized secret attachment still required"}
        elif args.command == "revise-interface":
            manifest = revised_pilot_manifest(args.campaign, args.description, args.authorization_reference)
            result = {"manifest_hash": digest(manifest), "status": "new source-bound coordinator GO required", "model_calls": 0}
        elif args.command == "freeze":
            result = freeze_live(args.campaign, args.pilot_stage)
        elif args.command == "audit-campaign":
            result = audit_campaign(args.campaign)
        elif args.command == "verify-evidence":
            result = verify_live_evidence(read_live_json(args.evidence))
        else:
            path = Path(args.campaign)
            name = (read_json(path / "freeze.json")["manifest_name"] if args.stage == "main"
                    else "manifest-v2.json" if args.stage == "pilot-v2" else "manifest.json")
            dataset, manifest = load_live(path, name, check_code=args.command in ("preflight", "acquire"))
            if args.command in ("preflight", "acquire"):
                go = read_json(args.go)
                validate_go(go, manifest, args.stage)
                if args.command == "preflight":
                    result = {"valid": True, "model_calls": 0, "manifest_hash": digest(manifest),
                              "worst_case_379_attempts_usd": manifest["worst_case_379_attempts_usd"],
                              "note": "No credential or network check; runtime rechecks pilot/freeze and shared wallet."}
                else:
                    run = run_live_stage(path, args.stage, go, api_key=os.environ.get("OPENROUTER_API_KEY"))
                    result = audit_live(dataset, manifest, run)
            else:
                run = read_live_json(path / args.stage / "run.json")
                if args.command == "audit":
                    result = audit_live(dataset, manifest, run)
                elif args.command == "pilot-gate":
                    previous = ([(load_live(path, check_code=False)[1], read_json(path / "pilot-v1" / "run.json"))]
                                if args.stage == "pilot-v2" else [])
                    result = live_pilot_gate(dataset, manifest, run, previous_pilots=previous)
                elif args.command == "analyze":
                    report = analyze_live(dataset, manifest, run)
                    write_new(args.out, report)
                    result = {"new_model_calls": report["new_model_calls"], "primary": report["primary_fault_S_minus_B"]}
                else:
                    evidence = export_live_evidence(dataset, manifest, run)
                    write_new(args.out, evidence)
                    result = verify_live_evidence(evidence)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (SchemaError, ValueError, OSError, KeyError, TypeError) as error:
        # No exception here carries request headers or a raw credential.
        print("ERROR: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())