"""Offline, bounded CLI. No credential discovery or hidden model routing."""

import argparse
from pathlib import Path

from .analysis import analyze, markdown_report
from .audit import audit
from .backends import TestDouble, test_config
from .environment import strict_json
from .protocol import canonical
from .runner import run_to_directory, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description="Summary-laundering engineering harness (no live model backend).")
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
    args = parser.parse_args(argv)
    if args.command == "access":
        print(canonical({
            "live_backend_available": False, "real_pilot_run": False, "empirical_protocol_frozen": False,
            "holdout_run": False, "required": [
                "explicit experimental provider/model and authorized interface",
                "applicable permission for a bounded batch and a monetary ceiling",
                "reviewed transport adapter with approved secret attachment, token/cost caps, and provider terms",
                "real development pilot before empirical freeze and holdout",
            ],
        }))
        return 0
    try:
        if args.command == "dry-run":
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
            print(canonical(audit(manifest, run) if args.command == "audit" else analyze(manifest, run)))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"error: {error}\n")
    return 0