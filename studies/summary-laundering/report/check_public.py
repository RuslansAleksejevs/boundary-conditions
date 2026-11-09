#!/usr/bin/env python3
"""Read-only replay of a schema-2 public export, without private logs or secrets.

Checks visible response parsing, mock state transitions, request identities and
primary statistics. This cannot authenticate provider acquisition or authorize a
new live experiment. Private wallet/GO/SSE audits remain a separate record.
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sl.analysis import condition_table, holm, paired
from sl.data import Scenario, extract
from sl.environment import evaluate, strict_json
from sl.live_run import validate_live_manifest
from sl.protocol import canonical, digest, executor_request, summary_request


def check(root):
    def read(name):
        return strict_json((root / name).read_text(encoding="utf-8"))
    manifest, report, campaign = read("manifest.json"), read("analysis.json"), read("campaign.json")
    if campaign["export_schema_version"] != 2:
        raise ValueError("full visible-response replay needs a schema-2 export; schema 1 was counts-only")
    validate_live_manifest(manifest, check_code=False)
    scenarios = {s["scenario_id"]: Scenario(**s) for s in manifest["scenarios"]}
    summaries = {s["scenario_id"]: s for s in read("summaries.json")}
    rows, calls = read("outcomes.json"), read("calls.json")
    if set(summaries) != set(scenarios) or len(rows) != len(scenarios) * 8:
        raise ValueError("incomplete public outcome/summaries matrix")
    by_call = {}
    for call in calls:
        sequence = by_call.setdefault(call["call_id"], [])
        if call["attempt"] != len(sequence) or len(sequence) >= 2:
            raise ValueError("public retry sequence is invalid")
        sequence.append(call)
        sid, arm = call["call_id"].split("/")
        scenario, summary = scenarios[sid], summaries[sid]
        if arm == "summary":
            request = summary_request(scenario)
        else:
            texts = {"R": scenario.raw}
            if summary["text"] is not None:
                texts.update(S=summary["text"], E=extract(scenario, summary["text"])[0])
            request = executor_request(scenario, arm, texts[arm[0]])
        if call["request_hash"] != digest({"request": request, "config": manifest["config"]}):
            raise ValueError("public request identity does not match the frozen synthetic input")
    for sid, summary in summaries.items():
        if summary["text"] is not None:
            sequence = by_call.get(sid + "/summary", [])
            if (not sequence or sequence[-1]["status"] != "completed"
                    or sequence[-1]["text"] != summary["text"] or summary["summary_hash"] != digest(summary["text"])):
                raise ValueError("public summary is not the recorded visible answer")
    seen = set()
    for row in rows:
        key = (row["scenario_id"], row["condition"])
        if key in seen or row["condition"] not in manifest["conditions"]:
            raise ValueError("duplicate or unknown public condition")
        seen.add(key)
        scenario, summary = scenarios[key[0]], summaries[key[0]]
        if (row["attacked"] is not scenario.attacked or row["family"] != scenario.family
                or row["cluster_id"] != scenario.cluster_id):
            raise ValueError("public outcome changed its frozen population or cluster")
        if row["summary_hash"] != (None if summary["text"] is None else digest(summary["text"])):
            raise ValueError("public replay changed the saved summary bytes")
        sequence = by_call.get("/".join(key), [])
        if sequence and sequence[-1]["status"] == "completed":
            text = sequence[-1]["text"]
            outcome = evaluate(text, scenario)
            for name, value in outcome.items():
                if canonical(row[name]) != canonical(value):
                    raise ValueError("public visible-response/state/score mismatch")
            if canonical(row["gate_replay"]) != canonical(evaluate(text, scenario, gate=True)):
                raise ValueError("public allowlist replay mismatch")
        elif row["score"] is not None:
            raise ValueError("public missing response has been assigned an outcome")
    if canonical(condition_table(rows)) != canonical(report["condition_table"]):
        raise ValueError("public condition table cannot be reproduced")
    attacked = [r for r in rows if r["attacked"]]
    options = {"draws": manifest["bootstrap"]["draws"], "seed": manifest["bootstrap"]["seed"]}
    primary = [paired(attacked, a, b, "effect", **options) for a, b in manifest["primary_contrasts"]]
    if all(p["exact_mcnemar_p"] is not None for p in primary):
        for result, adjusted in zip(primary, holm([p["exact_mcnemar_p"] for p in primary])):
            result["holm_two_primary_p"] = adjusted
    if canonical(primary) != canonical(report["primary"]):
        raise ValueError("public primary statistics cannot be reproduced")
    return {"public_replay_passed": True, "scenarios": len(scenarios), "outcomes": len(rows),
            "visible_call_records": len(calls), "primary_contrasts_reproduced": len(primary),
            "new_api_requests": 0, "provider_acquisition_authenticated": False,
            "scope": campaign["acquisition_scope"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("public_directory", type=Path)
    args = parser.parse_args()
    print(canonical(check(args.public_directory)))


if __name__ == "__main__":
    main()