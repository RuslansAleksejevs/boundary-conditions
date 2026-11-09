"""Offline, source-bound checks for the new reader report; no acquisition.

The scientific implementation and saved observations are read-only inputs.
``--write-new`` exclusively creates derived reporting assets. Normal invocation
recomputes them and compares bytes, including the separately preserved inventory.
"""

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent.parent
REPO = STUDY.parent.parent
sys.path.insert(0, str(STUDY))

from wgp.certificates import verify  # noqa: E402
from wgp.live import analyze_live, audit_campaign  # noqa: E402
from wgp.live_evidence import verify_live_evidence  # noqa: E402
from wgp.logic import render_expr, scalar, strict_json  # noqa: E402
from wgp.records import code_hashes  # noqa: E402
from wgp.vector import fidelity, tables, witness_valid  # noqa: E402


CAMPAIGN = STUDY / "results/live-main-2026-11-08"
BASE = "7e2780c1357dcb0ce14b749caf222fd1080bad06"
EDITABLE_OLD = {"README.md", "PLAN.md", "STATE.md", "HISTORY.md", "reports/README.md"}
EXAMPLES = ("holdout-fault-019", "holdout-equivalent-019")
REPO_URL = "https://github.com/RuslansAleksejevs/boundary-conditions"
PRINTED_MATH = (
    r"Original & $C=\neg r$ & $Q=(\neg r)\Rightarrow(s\lor p)$",
    r"Candidate & $C'=\neg r$ & $Q'=(s\lor p)\Rightarrow(\neg r)$",
    r"$C=q$ to $C'=q\land q$",
    r"Q=Q'=q\lor\bigl((p\land r)\lor(s\lor q)\bigr).",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return strict_json(Path(path).read_text(), max_bytes=512_000_000)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique_index(items, predicate):
    matches = [(i, item) for i, item in enumerate(items) if predicate(item)]
    require(len(matches) == 1, "source selector must identify exactly one record")
    return matches[0]


def displayed_values(case_id, state):
    """Independent, literal interpretations of the two printed examples.

    No AST traversal, vector evaluator, solver or generated expression execution.
    Return original C,Q and candidate C,Q. These are illustration checks, not
    a replacement for the frozen scientific scorer or new empirical outcomes.
    """
    p, q, r, s = (state[k] for k in ("p", "q", "r", "s"))
    if case_id == EXAMPLES[0]:
        return (not r, r or (s or p), not r, not (s or p) or not r)
    if case_id == EXAMPLES[1]:
        required = q or ((p and r) or (s or q))
        return (q, required, q and q, required)
    raise ValueError("example is not in the declared post-hoc selection")


def example(dataset, run, case_id, display=displayed_values):
    ci, case = unique_index(dataset["splits"]["holdout"], lambda x: x["id"] == case_id)
    original, candidate, cert = case["original"], case["candidate"], case["certificate"]
    require(verify(candidate, cert)["valid"], "candidate certificate is invalid")
    require(cert["verdict"] == "SAFE", "illustrated local verdict changed")
    rows = []
    oc, oq = tables(original)
    cc, cq = tables(candidate)
    for index, bits in enumerate(itertools.product((False, True), repeat=4)):
        state = dict(zip(("p", "q", "r", "s"), bits))
        literal = display(case_id, state)
        scalar_values = tuple(scalar(contract[field], state)
                              for contract in (original, candidate) for field in ("C", "Q"))
        vector_values = tuple(bool(table & (1 << index)) for table in (oc, oq, cc, cq))
        require(literal == scalar_values == vector_values,
                "printed interpretation differs from frozen semantics")
        rows.append({"state": state, "original_C": literal[0], "original_Q": literal[1],
                     "candidate_C": literal[2], "candidate_Q": literal[3]})
    original_failures = sum(r["original_C"] and not r["original_Q"] for r in rows)
    candidate_failures = sum(r["candidate_C"] and not r["candidate_Q"] for r in rows)
    require(candidate_failures == 0, "printed candidate has a counterexample")
    source_map = {"dataset.json": {"case": f"/splits/holdout/{ci}",
                                   "original": f"/splits/holdout/{ci}/original",
                                   "candidate": f"/splits/holdout/{ci}/candidate",
                                   "certificate": f"/splits/holdout/{ci}/certificate"},
                  "main/run.json": {}}
    answers = {}
    for arm in ("B", "N", "S"):
        oi, outcome = unique_index(run["outcomes"],
            lambda x: x["case_id"] == case_id and x["condition"] == arm)
        request_id = f"{case_id}:reviewer:{arm}"
        ri, call = unique_index(run["calls"], lambda x: x["request"]["id"] == request_id)
        payload = strict_json(call["request"]["user"])
        require(payload["original_task"] == case["task"] and payload["candidate"] == candidate
                and payload["certificate"] == cert, "example prompt/evidence binding changed")
        require(call["status"] == "completed" and outcome["status"] == "completed"
                and strict_json(call["response_text"]) == call["parsed"] == outcome["answer"]
                and outcome["correct"] and not outcome["false_safe"],
                "example answer/status binding changed")
        answer = outcome["answer"]
        if original_failures:
            require(answer["verdict"] == "UNSAFE"
                    and witness_valid(original, answer["witness"]), "original witness is false")
            values = display(case_id, answer["witness"])
            require(values[0] and not values[1], "printed witness does not refute original")
        else:
            require(answer == {"verdict": "SAFE", "witness": None}, "equivalent answer changed")
        answers[arm] = {"answer": answer, "response_text": call["response_text"]}
        source_map["main/run.json"][arm] = {
            "outcome": f"/outcomes/{oi}", "call": f"/calls/{ri}",
            "response_text": f"/calls/{ri}/response_text"}
    return {"case_id": case_id, "family": case["family"], "shown_condition": "B",
            "source_map": source_map, "original": original, "candidate": candidate,
            "certificate_hash": cert["contract_hash"], "certificate_rows": len(cert["rows"]),
            "original_admissible": sum(r["original_C"] for r in rows),
            "candidate_admissible": sum(r["candidate_C"] for r in rows),
            "original_failure_states": original_failures,
            "candidate_failure_states": candidate_failures,
            "fidelity": fidelity(original, candidate), "all_states": rows, "answers": answers}


def check_selection(dataset):
    for group, expected in zip(("fault", "equivalent"), EXAMPLES):
        candidates = [c for c in dataset["splits"]["holdout"] if c["group"] == group]
        score = lambda c: sum(len(render_expr(c[which][field]))
                              for which in ("original", "candidate") for field in ("C", "Q"))
        minimum = min(score(c) for c in candidates)
        shortest = [c["id"] for c in candidates if score(c) == minimum]
        require(shortest == [expected], "declared shortest-formula illustration selection changed")


def preservation_inventory():
    """First creation reads the existing base commit, never writes Git metadata."""
    prefix = "studies/wrong-goal-proof/"
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASE, "--", prefix], cwd=REPO, text=True).splitlines()
    inventory = {}
    for path in paths:
        relative = path.removeprefix(prefix)
        if relative in EDITABLE_OLD:
            continue
        blob = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=REPO)
        inventory[relative] = hashlib.sha256(blob).hexdigest()
    return {"base_commit": BASE, "algorithm": "SHA256 bytes",
            "scope": "Every preexisting study file except the five explicitly editable navigation/state files.",
            "files": inventory}


def verify_preserved(inventory):
    require(inventory["base_commit"] == BASE, "preservation baseline changed")
    for relative, expected in inventory["files"].items():
        require(sha(STUDY / relative) == expected, "preserved file changed: " + relative)
    return len(inventory["files"])


def collect():
    dataset, manifest = read(CAMPAIGN / "dataset.json"), read(CAMPAIGN / "manifest.json")
    require(manifest["code_hashes"] == code_hashes(), "frozen scientific source changed")
    check_selection(dataset)
    audit = audit_campaign(CAMPAIGN)
    require(audit["valid"] and audit["physical_attempts"] == 310, "native campaign audit failed")
    runs, analyses, stage_rows = {}, {}, []
    for stage, split, label in (("pilot-v1", "dev", "Pilot"), ("main", "holdout", "Held-out main")):
        run, saved = read(CAMPAIGN / stage / "run.json"), read(CAMPAIGN / stage / "analysis.json")
        require(analyze_live(dataset, manifest, run) == saved, "saved analysis differs from replay")
        packet = verify_live_evidence(read(CAMPAIGN / stage / "evidence.json"))
        require(packet["independently_confirmed_false_guarantees"] == 0, "evidence count changed")
        runs[stage], analyses[stage] = run, saved
        groups = Counter(c["group"] for c in dataset["splits"][split])
        statuses = Counter(c["status"] for c in run["calls"])
        stage_rows.append({"stage": label, "originals": sum(groups.values()),
            "natural": groups["natural"], "planted": groups["fault"], "equivalent": groups["equivalent"],
            "scheduled_roles": run["scheduled_calls"], "valid_roles": statuses["completed"],
            "invalid_roles": statuses["schema_error"], "blocked_roles": statuses["blocked_translation"],
            "physical_attempts": len(run["receipts"]),
            "known_cost_attempts": saved["usage"]["cost_usd"]["known_attempts"],
            "unknown_cost_attempts": len(run["receipts"]) - saved["usage"]["cost_usd"]["known_attempts"]})
    main = runs["main"]
    outcome_rows = []
    for group, label in (("natural", "Natural"), ("fault", "Planted"), ("equivalent", "Equivalent")):
        for arm in (("B",) if group == "natural" else ("B", "N", "S")):
            selected = [o for o in main["outcomes"] if o["group"] == group and o["condition"] == arm]
            statuses = Counter(o["status"] for o in selected)
            outcome_rows.append({"population": label, "arm": arm, "scheduled": len(selected),
                "correct": sum(o["correct"] for o in selected),
                "false_safe": sum(o["false_safe"] for o in selected), "assessed": statuses["completed"],
                "invalid_reviews": statuses["schema_error"], "blocked_reviews": statuses["blocked_translation"],
                "other_missing": sum(v for k, v in statuses.items()
                                     if k not in ("schema_error", "blocked_translation", "completed")),
                "abstentions": sum(o["abstained"] for o in selected)})
    operational = read(STUDY / "reports/main/operational-summary.json")
    known = sum((Decimal(str(receipt["response"]["usage"]["cost"]))
                 for run in runs.values() for receipt in run["receipts"]
                 if receipt["http_status"] == 200), Decimal(0))
    require(known == Decimal(operational["campaign_reported_api_cost_usd"]["known_sum"]),
            "reported-cost subtotal changed")
    examples = [example(dataset, main, cid) for cid in EXAMPLES]
    source_files = ["dataset.json", "manifest.json", "freeze.json", "budget.jsonl"]
    source_files += [f"{stage}/{name}.json" for stage in runs for name in ("run", "analysis", "evidence")]
    return {"kind": "derived_reader_report_checks_not_new_experiment", "new_api_requests": 0,
        "selection": "Post-hoc clarity selection: the shortest combined rendered formulas in each of the planted and equivalent groups; B is shown. Not a frequency sample.",
        "frozen_source_commit": manifest["code_revision"],
        "source_file_sha256": {name: sha(CAMPAIGN / name) for name in source_files},
        "operational_summary_sha256": sha(STUDY / "reports/main/operational-summary.json"),
        "stages": stage_rows, "main_outcomes": outcome_rows,
        "paired": {key: analyses["main"][key] for key in
                   ("primary_fault_S_minus_B", "secondary_fault_N_minus_B", "equivalent_utility_S_minus_B")},
        "natural_drift": analyses["main"]["natural_drift_among_valid_translations"],
        "natural_missingness_bounds": analyses["main"]["groups"]["natural"]["B"]["full_sample_false_safe_bounds"],
        "known_campaign_cost_usd": str(known),
        "unknown_holds_usd": operational["stages"]["main"]["stage_wallet"]["unknown_holds_usd"],
        "wallet_commitment_usd": operational["stages"]["main"]["cumulative_wallet_through_stage"]["committed_usd"],
        "examples": examples}


def render_assets(data):
    stages = []
    for row in data["stages"]:
        counts = f'{row["natural"]}/{row["planted"]}/{row["equivalent"]}'
        stages.append(f'{row["stage"]} & {counts} & {row["valid_roles"]}/{row["scheduled_roles"]}'
                      f' & {row["invalid_roles"]}/{row["blocked_roles"]} & {row["physical_attempts"]} \\\\')
    outcomes = []
    for row in data["main_outcomes"]:
        outcomes.append(f'{row["population"]} {row["arm"]} & {row["correct"]}/{row["scheduled"]}'
                        f' & {row["false_safe"]}/{row["assessed"]} & {row["invalid_reviews"]}'
                        f' & {row["blocked_reviews"]} \\\\')
    contrasts = []
    for key, label in (("primary_fault_S_minus_B", "Scoped $-$ PASS (primary)"),
                       ("secondary_fault_N_minus_B", "Neutral $-$ PASS (secondary)")):
        row = data["paired"][key]
        low, high = (100 * value for value in row["bounded_iid_hoeffding95"])
        contrasts.append(f'{label} & {row["complete_pairs"]}/{row["scheduled_pairs"]}'
                         f' & {100 * row["difference"]:.0f} & [{low:.2f}, {high:.2f}] \\\\')
    return {"report-data.json": json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n",
            "stage-rows.tex": "\n".join(stages) + "\n",
            "outcome-rows.tex": "\n".join(outcomes) + "\n",
            "contrast-rows.tex": "\n".join(contrasts) + "\n"}


def check_document(data):
    text = (HERE / "verified-but-what.tex").read_text()
    require(REPO_URL in text and text.index(REPO_URL) < text.index(r"\begin{abstract}"),
            "clickable repository URL must precede abstract")
    for item in data["examples"]:
        require(item["case_id"] in text, "printed example ID missing")
        require(item["answers"]["B"]["response_text"] in text, "exact B response quote missing")
    for formula in PRINTED_MATH:
        require(text.count(formula) == 1, "checked printed formula missing or duplicated")
    for phrase in ("Limitations and Dual-Use / Ethical Considerations", "LLM Usage Statement",
                   "pending human review"):
        require(phrase in text, "required disclosure missing: " + phrase)
    for forbidden in ("companion", "Study A", "summary-laundering", "USD50", "USD 50", "/Users/"):
        require(forbidden.lower() not in text.lower(), "out-of-scope/private wording: " + forbidden)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-new", action="store_true", help="exclusively create derived report assets")
    args = parser.parse_args()
    inventory_path = HERE / "preserved-files.json"
    inventory = preservation_inventory() if args.write_new else read(inventory_path)
    preserved = verify_preserved(inventory)
    data = collect()
    assets = render_assets(data)
    if args.write_new:
        assets["preserved-files.json"] = json.dumps(inventory, indent=2, sort_keys=True) + "\n"
        require(not any((HERE / name).exists() for name in assets), "derived output already exists")
        for name, content in assets.items():
            with (HERE / name).open("x") as stream:
                stream.write(content)
    else:
        for name, content in assets.items():
            require((HERE / name).read_text() == content, "derived report asset changed: " + name)
        check_document(data)
    print(json.dumps({"reader_checks_passed": True, "new_api_requests": 0,
        "preserved_files": preserved, "examples": len(data["examples"]),
        "states_checked_per_example": 16, "example_conditions_checked": 6,
        "main_outcome_cells": sum(r["scheduled"] for r in data["main_outcomes"]),
        "historical_physical_attempts_replayed": 310, "provider_authenticated": False}))


if __name__ == "__main__":
    main()