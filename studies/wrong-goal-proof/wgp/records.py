"""Immutable local bundles and freeze records; hashes are integrity, not attestation."""

import hashlib
import platform
import subprocess
from pathlib import Path

from .adapters import TranscriptAdapter
from .dataset import audit_dataset, make_dataset
from .logic import SchemaError, digest, strict_json
from .pipeline import audit_run, pilot_gate, timestamp
from .prompts import prompt_spec, review_request, translation_request


STUDY_ROOT = Path(__file__).resolve().parent.parent


def read_json(path, max_bytes=30_000_000):
    path = Path(path)
    if path.stat().st_size > max_bytes:
        raise SchemaError("local JSON record exceeds its bounded file size")
    text = path.read_text(encoding="utf-8")
    # Same strict decoder; local bundles are larger than a single model response.
    return strict_json(text, max_bytes=max_bytes)


def write_new(path, value):
    import json
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def code_hashes():
    paths = sorted(STUDY_ROOT.glob("wgp/*.py")) + sorted(STUDY_ROOT.glob("tests/*.py"))
    paths += sorted(STUDY_ROOT.glob("tests/fixtures/*.json"))
    paths += [STUDY_ROOT / "run.py"] + sorted(STUDY_ROOT.glob("run_live.py"))
    return {str(path.relative_to(STUDY_ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def git_revision():
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=STUDY_ROOT,
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def prepare(path, seed=6006):
    path = Path(path)
    if path.exists():
        raise FileExistsError("bundle output already exists; choose a new path")
    dataset = make_dataset(seed)
    manifest = {"version": 1, "status": "prepared_not_experimental_freeze",
                "created_at": timestamp(), "python": platform.python_version(),
                "git_revision_at_preparation": git_revision(),
                "code_hashes": code_hashes(), "dataset_hash": digest(dataset),
                "prompt_spec": prompt_spec(), "seed": seed,
                "case_ids": {split: [case["id"] for case in cases]
                             for split, cases in dataset["splits"].items()},
                "scheduled_calls": {"dev": 52, "holdout": 260},
                "limits": {"max_retries_per_call": 0, "concurrency": 1,
                           "network_calls_supported": False, "new_paid_calls_authorized": False,
                           "monetary_limit_usd": 0, "response_max_bytes": 200_000},
                "analysis": {"primary": "fault false_SAFE S-B", "secondary": "fault N-B",
                             "unit": "original contract", "bootstrap_samples": 5000,
                             "bootstrap_seed": 606, "missing_policy": "unassessed; never safe-imputed",
                             "natural_and_planted_pooled": False},
                "ground_truth_audit": audit_dataset(dataset)}
    write_new(path / "dataset.json", dataset)
    write_new(path / "manifest.json", manifest)
    return manifest


def load_bundle(path, check_code=True):
    path = Path(path)
    dataset, manifest = read_json(path / "dataset.json"), read_json(path / "manifest.json")
    audit_dataset(dataset)
    if manifest["dataset_hash"] != digest(dataset):
        raise SchemaError("dataset hash mismatch")
    if manifest["prompt_spec"] != prompt_spec():
        raise SchemaError("prompt specification changed")
    if check_code and manifest["code_hashes"] != code_hashes():
        raise SchemaError("source/tests changed since preparation; create a new development bundle")
    if manifest["case_ids"] != {s: [c["id"] for c in cases] for s, cases in dataset["splits"].items()}:
        raise SchemaError("case manifest mismatch")
    return dataset, manifest


def freeze(path, pilot_path, output):
    dataset, manifest = load_bundle(path)
    pilot = read_json(pilot_path)
    if pilot["manifest_hash"] != digest(manifest):
        raise SchemaError("pilot bound to different manifest")
    gate = pilot_gate(dataset, pilot)
    if not gate["passed"]:
        raise SchemaError("pilot stop rule failed; preserve run and do not evaluate holdout")
    frozen = {"version": 1, "created_at": timestamp(), "manifest_hash": digest(manifest),
              "dataset_hash": digest(dataset), "pilot_hash": digest(pilot), "pilot_gate": gate,
              "adapter": pilot["adapter"], "code_hashes": code_hashes(),
              "status": ("synthetic_freeze_rehearsal" if pilot["adapter"]["kind"] ==
                         "synthetic_test_double" else "offline_transcript_freeze"),
              "not_public_preregistration": True,
              "warning": "Offline timestamps/hashes do not attest when external responses were acquired."}
    write_new(output, frozen)
    return frozen


def verify_freeze(frozen, manifest, adapter):
    if (frozen["manifest_hash"] != digest(manifest)
            or frozen["dataset_hash"] != manifest["dataset_hash"]
            or frozen["code_hashes"] != code_hashes()
            or frozen["adapter"] != adapter.configuration
            or not frozen["pilot_gate"]["passed"]):
        raise SchemaError("freeze/configuration mismatch")


def load_transcript(path):
    value = read_json(path)
    from .logic import keys
    keys(value, ("metadata", "entries"))
    return TranscriptAdapter(value["entries"], value["metadata"])


def initial_requests(dataset, split):
    """No translator oracle shortcut. A's reviewer request needs an actual translation."""
    result = []
    for case in dataset["splits"][split]:
        if case["group"] == "natural":
            result.append(translation_request(case))
        else:
            for condition in ("B", "N", "S"):
                result.append(review_request(case, case["candidate"], case["certificate"], condition))
    return result
