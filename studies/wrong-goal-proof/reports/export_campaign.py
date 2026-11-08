"""Export a completed synthetic-task campaign without changing audited records.

No model, credential or network access. Raw append-only intent/event journals,
host paths, account responses and unrelated files are never copied. The reviewed
visible acquisition records remain internally auditable, not provider-signed.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wgp.live import (analyze_live, audit_campaign, audit_live, live_pilot_gate,
                      load_live, read_json)
from wgp.live_evidence import export_live_evidence
from wgp.logic import canonical, digest
from wgp.pipeline import timestamp
from wgp.records import write_new


PRIVATE_PATTERNS = (
    ("host path", re.compile(r"/(?:Users|home)/")),
    ("credential prefix", re.compile(r"\bsk-(?:or-v1-|proj-)")),
    ("private coordination identifier", re.compile(r"\bs[0-9a-f]{21,32}\b")),
    ("authorization header", re.compile(r'"[Aa]uthorization"\s*:\s*"[Bb]earer ')),
)


def privacy_check(value):
    text = canonical(value)
    for category, pattern in PRIVATE_PATTERNS:
        if pattern.search(text):
            raise ValueError("publication blocked by " + category + "; review privately, do not auto-redact")


def export_campaign(source, target):
    source, target = Path(source), Path(target)
    if not (source / "main" / "run.json").is_file():
        raise ValueError("do not publish the held-out corpus before main acquisition ends")
    source_audit = audit_campaign(source)
    frozen = read_json(source / "freeze.json")
    # The selected frozen revision, not necessarily the first failed pilot's
    # revision, must match the current acquisition source.
    load_live(source, frozen["manifest_name"], check_code=True)
    dataset, original_manifest = load_live(source, check_code=False)
    files = {"dataset.json": dataset, "manifest.json": original_manifest, "freeze.json": frozen}
    if (source / "manifest-v2.json").exists():
        files["manifest-v2.json"] = load_live(source, "manifest-v2.json")[1]
    prior = []
    for stage in ("pilot-v1", "pilot-v2", "main"):
        if stage not in source_audit["stages"]:
            continue
        name = frozen["manifest_name"] if stage == "main" else "manifest-v2.json" if stage == "pilot-v2" else "manifest.json"
        manifest = files[name]
        run = read_json(source / stage / "run.json")
        files[stage + "/run.json"] = run
        files[stage + "/analysis.json"] = analyze_live(dataset, manifest, run)
        files[stage + "/evidence.json"] = export_live_evidence(dataset, manifest, run)
        files[stage + "/audit.json"] = audit_live(dataset, manifest, run)
        if stage != "main":
            files[stage + "/gate.json"] = live_pilot_gate(dataset, manifest, run, previous_pilots=prior)
            prior.append((manifest, run))
    files["campaign-audit.json"] = source_audit
    ledger = (source / "budget.jsonl").read_text(encoding="utf-8")
    # Only audited objects and the exact audited wallet are published. If a
    # privacy check fails, preserve the source and stop; never silently change a
    # response, approval reference or hash to make a record appear publishable.
    for value in files.values():
        privacy_check(value)
    for line in ledger.splitlines():
        privacy_check(json.loads(line))
    target.mkdir(parents=True, exist_ok=False)
    for name, value in files.items():
        write_new(target / name, value)
    with (target / "budget.jsonl").open("x", encoding="utf-8") as stream:
        stream.write(ledger)
    if audit_campaign(target) != source_audit:
        raise ValueError("public copy failed the unchanged campaign audit; preserve for diagnosis")
    inventory = {}
    for name in sorted([*files, "budget.jsonl"]):
        data = (target / name).read_bytes()
        inventory[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        if name in files:
            inventory[name]["canonical_digest"] = digest(files[name])
    record = {
        "version": 1, "exported_at": timestamp(), "kind": "actual_visible_synthetic_task_campaign",
        "new_calls_sent_by_export": 0, "source_and_export_audit_equal": True,
        "new_model_calls_in_original_acquisition": source_audit["new_model_calls"],
        "provider_hidden_reasoning_fields_removed": True,
        "raw_event_journals_exported": False, "private_account_records_exported": False,
        "provider_acquisition_ids": "Original opaque technical generation IDs retained for receipt consistency; not credentials.",
        "privacy_review": "Known host-path, credential-prefix, coordination-ID and authorization-header scans passed; manual content review still required.",
        "provenance_authenticated": False,
        "claim_limit": "Hashes and replay validate local consistency and mathematics, not cryptographic provider origin or public preregistration.",
        "files": inventory,
    }
    privacy_check(record)
    write_new(target / "EXPORT.json", record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = export_campaign(args.campaign, args.out)
    print(json.dumps({"files": len(record["files"]), "new_calls_sent_by_export": 0,
                      "original_model_calls": record["new_model_calls_in_original_acquisition"],
                      "audit_equal": True}, indent=2))


if __name__ == "__main__":
    main()