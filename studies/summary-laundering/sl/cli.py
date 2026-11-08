"""Offline validation and explicitly authorized bounded live acquisition."""

import argparse
from pathlib import Path

from .analysis import analyze, markdown_report
from .audit import audit
from .backends import TestDouble, test_config
from .environment import strict_json
from .protocol import canonical
from .runner import run_to_directory, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description="Summary-laundering harness: offline tests and separately authorized live acquisition.")
    commands = parser.add_subparsers(dest="command", required=True)
    dry = commands.add_parser("dry-run", help="deterministic test-double pipeline, never model evidence")
    dry.add_argument("--split", choices=("dev", "validation"), default="dev")
    dry.add_argument("--seed", type=int, default=1701)
    dry.add_argument("--profile", choices=TestDouble.profiles, default="scripted")
    dry.add_argument("--out", type=Path, required=True, help="new private output directory; never overwritten")
    for name in ("analyze", "audit"):
        command = commands.add_parser(name)
        command.add_argument("run_directory", type=Path)
    commands.add_parser("access", help="show the exact live-experiment blocker")
    prepare = commands.add_parser("live-prepare", help="write an immutable prospective acquisition plan; no API call")
    prepare.add_argument("--config", type=Path, required=True)
    prepare.add_argument("--phase", choices=("pilot", "pilot_repair", "main"), required=True)
    prepare.add_argument("--seed", type=int, required=True)
    prepare.add_argument("--pilot", type=Path)
    prepare.add_argument("--repair-reason")
    prepare.add_argument("--out", type=Path, required=True)
    wallet = commands.add_parser("live-wallet", help="create the one shared per-study spend ledger; no API call")
    wallet.add_argument("--config", type=Path, required=True)
    wallet.add_argument("--out", type=Path, required=True)
    acquire_command = commands.add_parser("live-acquire", help="paid acquisition: requires exact coordinator preflight GO and secret attachment")
    for name in ("plan", "go", "ledger", "out"):
        acquire_command.add_argument("--" + name, type=Path, required=True)
    acquire_command.add_argument("--pilot", type=Path, help="actual prior pilot directory; mandatory for main/repair")
    continuation_plan = commands.add_parser("continuation-prepare", help="plan the explicit untouched-suffix operational amendment; no API calls")
    continuation_plan.add_argument("--parent", type=Path, required=True)
    continuation_plan.add_argument("--out", type=Path, required=True)
    continuation = commands.add_parser("continuation-acquire", help="one source-bound, paced continuation; never resamples attempted roles")
    for name in ("parent", "plan", "go", "ledger", "out"):
        continuation.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "access":
        print(canonical({
            "live_backend_available": True, "acquisition_requires_coordinator_go": True,
            "experiment_status": "not inferred without an audited run directory",
            "credentials_checked": False, "required": [
                "explicit experimental provider/model and authorized interface",
                "applicable permission for a bounded batch and a monetary ceiling",
                "coordinator preflight GO bound to config and an approved secret attachment",
                "real development pilot before empirical freeze and holdout",
            ],
        }))
        return 0
    try:
        if args.command == "continuation-prepare":
            from .continuation import make_continuation_plan
            manifest = strict_json((args.parent / "manifest.json").read_text(encoding="utf-8"))
            parent = strict_json((args.parent / "run.json").read_text(encoding="utf-8"))
            plan = make_continuation_plan(manifest, parent)
            write_json(args.out, plan)
            print(canonical({"plan_hash": plan["plan_hash"], "new_request_cap": plan["new_request_cap"],
                             "new_model_calls": 0, "maximum_possible_valid_roles": plan["maximum_possible_valid_roles"]}))
        elif args.command == "continuation-acquire":
            from .continuation import acquire_continuation
            manifest, run = acquire_continuation(args.parent, args.plan, args.go, args.ledger, args.out)
            report = analyze(manifest, run)
            write_json(args.out / "analysis.json", report)
            print(canonical({"audit": report["audit"], "amended_composite_gate": report["pilot_gate"],
                             "new_api_requests": len(run["calls"]) - len(run["continuation"]["parent_run"]["calls"]),
                             "stop_reason": run["stop_reason"]}))
        elif args.command == "live-prepare":
            from .live_run import live_gate, live_manifest
            from .continuation import effective_pilot_sources
            from .protocol import digest
            config = strict_json(args.config.read_text(encoding="utf-8"))
            pilot = None
            if args.pilot:
                pilot_manifest = strict_json((args.pilot / "manifest.json").read_text(encoding="utf-8"))
                pilot_run = strict_json((args.pilot / "run.json").read_text(encoding="utf-8"))
                pilot = {"manifest": pilot_manifest, "gate": live_gate(pilot_manifest, pilot_run), "run_hash": digest(pilot_run)}
                pilot["acquisition_code_hashes"] = effective_pilot_sources(pilot_manifest, pilot_run)
                pilot["continuation_plan_hash"] = pilot_run.get("continuation", {}).get("plan", {}).get("plan_hash")
            manifest = live_manifest(config, args.phase, args.seed, pilot=pilot, repair_reason=args.repair_reason)
            write_json(args.out, manifest)
            print(canonical({"manifest_hash": manifest["manifest_hash"], "planned_requests": manifest["planned_requests"],
                             "maximum_campaign_reservation_usd": manifest["maximum_campaign_reservation_usd"], "new_model_calls": 0}))
        elif args.command == "live-wallet":
            from .live_transport import Ledger
            config = strict_json(args.config.read_text(encoding="utf-8"))
            Ledger(args.out, config, create=True)
            print(canonical({"ledger_created": True, "new_model_calls": 0}))
        elif args.command == "live-acquire":
            from .live_run import acquire
            manifest, run = acquire(args.plan, args.go, args.ledger, args.out, args.pilot)
            report = analyze(manifest, run)
            write_json(args.out / "analysis.json", report)
            print(canonical({"audit": report["audit"], "evidence_label": report["evidence_label"],
                             "external_api_requests": report["cost"]["external_api_requests"], "stop_reason": run["stop_reason"]}))
        elif args.command == "dry-run":
            manifest, run = run_to_directory(args.out, args.split, args.seed, test_config(args.profile))
            report = analyze(manifest, run)
            write_json(args.out / "analysis.json", report)
            with (args.out / "REPORT.md").open("x", encoding="utf-8") as stream:
                stream.write(markdown_report(report))
            print(canonical({"evidence_label": report["evidence_label"], "audit": report["audit"],
                             "external_api_requests": 0, "retries": run["retries_used"]}))
        else:
            manifest = strict_json((args.run_directory / "manifest.json").read_text(encoding="utf-8"))
            run = strict_json((args.run_directory / "run.json").read_text(encoding="utf-8"))
            if args.command == "audit" and manifest["backend_kind"] == "openrouter_live":
                from .live_run import audit_live
                print(canonical(audit_live(manifest, run)))
            else:
                print(canonical(audit(manifest, run) if args.command == "audit" else analyze(manifest, run)))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"error: {error}\n")
    return 0