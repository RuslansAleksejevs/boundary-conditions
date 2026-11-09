#!/usr/bin/env python3
"""Build/check reader-report tables and exact examples. No network or inference.

Only --render writes, and only three derived files beside this script. Original
experimental files, scientific modules and historical reports are never changed.
"""

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parents[1]
sys.path[:0] = [str(STUDY), str(HERE.parent)]

from check_public import check as public_check
from sl.environment import parse_actions
from sl.protocol import canonical, digest
from sl.runner import code_hashes

MAIN = STUDY / "results/main-2026-11-09"
PILOT = STUDY / "results/pilot-composite-2026-11-08"
EXAMPLE_IDS = ("live-main-2026110812-020-attack", "live-main-2026110812-008-attack")
FROZEN_INVENTORY = "dbb21522554b9c96bed164d89230f6ecbb36b7d51b2861048f275a6461c424ca"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def tex(text):
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
                    "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{",
                    "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(c, c) for c in str(text))


def counts(rows):
    observed = [r for r in rows if r["score"] is not None]
    return {"scheduled": len(rows), "observed": len(observed),
            "missing": len(rows) - len(observed),
            **{k: sum(r["score"][k] for r in observed)
               for k in ("effect", "attempt", "task_correct", "valid_response", "abstained")},
            "invalid": sum(not r["score"]["valid_response"] for r in observed)}


def source_record(filename, items, index, fields):
    return {"file": str((MAIN / filename).relative_to(STUDY)),
            "selector": {k: items[index][k] for k in ("scenario_id", "call_id", "condition", "attempt")
                         if k in items[index]},
            "pointers": {field: f"/{index}/{field}" for field in fields}}


def example(manifest, summaries, rows, calls, sid):
    si = next(i for i, s in enumerate(manifest["scenarios"]) if s["scenario_id"] == sid)
    ui = next(i for i, s in enumerate(summaries) if s["scenario_id"] == sid)
    ri = next(i for i, r in enumerate(rows) if (r["scenario_id"], r["condition"]) == (sid, "S-P"))
    ci = max(i for i, c in enumerate(calls) if c["call_id"] == sid + "/S-P")
    scenario, summary, outcome, call = manifest["scenarios"][si], summaries[ui], rows[ri], calls[ci]
    assert outcome["summary_hash"] == summary["summary_hash"] == digest(summary["text"])
    assert call["request_hash"] == outcome["request_hash"]
    task = scenario["task_id"]
    record_source = source_record("manifest.json", manifest["scenarios"], si,
                                  ("task", "paragraph", "facts", "answer"))
    record_source["pointers"] = {k: "/scenarios" + v for k, v in record_source["pointers"].items()}
    return {"scenario_id": sid, "condition": "S-P", "task_id": task,
            "facts_verbatim": scenario["facts"], "record_paragraph_verbatim": scenario["paragraph"],
            "summary_verbatim": summary["text"], "response_verbatim": call["text"],
            "gold_answer": scenario["answer"], "score": outcome["score"],
            "parse_error": outcome["parse_error"], "actions": outcome["actions"],
            "events_count": len(outcome["events"]),
            "answer_before": outcome["initial_state"]["results"][task]["answer"],
            "answer_after": outcome["final_state"]["results"][task]["answer"],
            "approved_before": outcome["initial_state"]["protected"][task]["approved"],
            "approved_after": outcome["final_state"]["protected"][task]["approved"],
            "sources": [record_source,
                        source_record("summaries.json", summaries, ui, ("text", "summary_hash")),
                        source_record("outcomes.json", rows, ri, ("score", "actions", "events", "initial_state", "final_state")),
                        source_record("calls.json", calls, ci, ("text", "request_hash"))]}


def derive():
    replay = {"main": public_check(MAIN), "pilot": public_check(PILOT)}
    assert digest(code_hashes()) == FROZEN_INVENTORY
    manifest, report = load(MAIN / "manifest.json"), load(MAIN / "analysis.json")
    rows, summaries, calls = (load(MAIN / name) for name in ("outcomes.json", "summaries.json", "calls.json"))
    campaign = load(MAIN / "campaign.json")
    pilot_rows = load(PILOT / "outcomes.json")
    pilot_report = load(PILOT / "analysis.json")
    failed_report = load(MAIN / "failed-pilot-analysis.json")
    first, second = [example(manifest, summaries, rows, calls, sid) for sid in EXAMPLE_IDS]
    assert EXAMPLE_IDS[0] == min(s["scenario_id"] for s in manifest["scenarios"]
                                 if s["attacked"] and s["family"] == "prerequisite")
    assert EXAMPLE_IDS[1] == min(r["scenario_id"] for r in rows if r["attacked"]
                                 and r["condition"] == "S-P" and r["status"] == "invalid_response")
    prefix = first["summary_verbatim"].split(" The record identifies itself", 1)[0]
    target = "protected[" + first["task_id"] + "].approved"
    assert target + " is set to true" in prefix
    assert first["score"]["task_correct"] and not first["score"]["effect"]
    assert len(first["actions"]) == 1 and first["actions"][0]["store"] == "results"
    assert first["answer_after"] == first["gold_answer"] == "Q38337X"
    assert first["approved_before"] is False and first["approved_after"] is False
    first["summary_excerpt_verbatim"] = prefix
    first["selection_note"] = "Existing frozen first prerequisite-family trace; selected here to explain visible instruction retention."
    assert second["response_verbatim"].startswith("```json\n") and second["response_verbatim"].endswith("\n```")
    assert parse_actions(second["response_verbatim"]) == (None, "invalid_json")
    assert not second["score"]["valid_response"] and not second["score"]["task_correct"]
    assert second["actions"] == [] and second["events_count"] == 0 and second["answer_after"] is None
    assert '"value": "Q46410X"' in second["response_verbatim"]
    assert r"\end{verbatim}" not in second["response_verbatim"]
    second["selection_note"] = "Post-hoc illustration: lexicographically first attacked S-P invalid response. No frequency or causal estimate."
    source_files = {str(p.relative_to(STUDY)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for root in (MAIN, PILOT) for p in sorted(root.glob("*.json"))}
    result = {"purpose": "Reader-report derivation only; no new experiment or regrading.",
              "source_inventory": FROZEN_INVENTORY, "source_files_sha256": source_files,
              "public_replay": replay, "main": counts(rows), "pilot": counts(pilot_rows),
              "main_inputs": len(manifest["scenarios"]),
              "main_clusters": len({s["cluster_id"] for s in manifest["scenarios"]}),
              "main_valid_summaries": sum(s["status"] == "completed" for s in summaries),
              "main_physical_requests": len(calls), "main_scheduled_roles": manifest["planned_requests"],
              "main_retry_requests": sum(c["attempt"] for c in calls),
              "main_call_statuses": dict(Counter(c["status"] for c in calls)),
              "main_parse_errors": dict(Counter(r["parse_error"] for r in rows if r.get("parse_error"))),
              "condition_table": report["condition_table"], "primary": report["primary"],
              "secondary": report["secondary"], "length_matching": report["length_matching"],
              "pilot_gate": pilot_report["pilot_gate"], "campaign": campaign,
              "failed_pilot": {"gate": failed_report["pilot_gate"],
                               "scheduled_executor_cells": sum(r["scheduled"] for r in failed_report["condition_table"]),
                               "observed_executor_cells": sum(r["metrics"]["effect"]["observed"] for r in failed_report["condition_table"])},
              "examples": [first, second], "new_api_requests": 0}
    assert result["main"]["scheduled"] == 480 and result["main_clusters"] == 40
    return result


def interval(values):
    return "[" + ", ".join(f"{v:.2f}" for v in values) + "]"


def render(data):
    main, pilot, campaign = data["main"], data["pilot"], data["campaign"]
    macros = {"MainCorrect": main["task_correct"], "MainScheduled": main["scheduled"],
              "MainObserved": main["observed"], "MainValid": main["valid_response"],
              "MainInvalid": main["invalid"], "MainMissing": main["missing"],
              "MainAbstentions": main["abstained"], "MainEffects": main["effect"],
              "MainCalls": data["main_physical_requests"], "MainRoles": data["main_scheduled_roles"],
              "MainInputs": data["main_inputs"], "MainClusters": data["main_clusters"],
              "MainRetries": data["main_retry_requests"], "StudyCalls": campaign["total_actual_requests"],
              "StudyKnownCost": f'{Decimal(campaign["accounted_billed_cost_usd"]):.2f}',
              "StudyWallet": f'{Decimal(campaign["charged_or_reserved_usd"]):.2f}',
              "UnresolvedCosts": campaign["additional_unresolved_cost_calls"],
              "RetainedHolds": sum(s["unknown_receipt_cost_calls"] for s in campaign["stages"]),
              "LengthUnmatched": data["length_matching"]["unmatched"]}
    for label, arm in (("Warning", "S-P-W"), ("Provenance", "S-P-P")):
        comparison = next(r for r in data["secondary"] if r["population"] == "attacked"
                          and r["metric"] == "task_correct" and r["a"] == arm and r["b"] == "S-P")
        macros[label + "Utility"] = f'{comparison["difference_pp"]:+.2f}'
        macros[label + "Bootstrap"] = interval(comparison["cluster_bootstrap_95_ci_pp"])
    out = ["% Derived from immutable public evidence by evidence.py --render."]
    out += ["\\newcommand{\\" + key + "}{" + tex(value) + "}" for key, value in macros.items()]
    table = []
    for condition in ("R-D", "R-P", "E-D", "E-P", "S-D", "S-P", "S-P-W", "S-P-P"):
        cells = [condition]
        for attacked in (True, False):
            row = next(r for r in data["condition_table"] if r["condition"] == condition and r["attacked"] == attacked)
            utility, effect = row["metrics"]["task_correct"], row["metrics"]["effect"]
            cells += [f'{utility["events"]}/{row["scheduled"]}', f'{effect["events"]}/{effect["observed"]}',
                      str(row["scheduled"] - effect["observed"])]
        table.append(" & ".join(cells) + r" \\")
    out += [r"\newcommand{\ConditionRows}{", *table, "}"]
    primary = []
    for row in data["primary"]:
        label = "Source label: S-P $-$ S-D" if row["b"] == "S-D" else "Content: S-P $-$ E-P"
        primary.append(" & ".join([label, f'{row["complete_pairs"]}/{row["scheduled_pairs"]}',
                                   f'{row["difference_pp"]:.2f}', interval(row["bounded_independent_cluster_95_ci_pp"]),
                                   interval(row["scheduled_difference_bounds_pp"])]) + r" \\")
    out += [r"\newcommand{\PrimaryRows}{", *primary, "}"]
    stages = campaign["stages"]
    failed = data["failed_pilot"]
    assert failed["observed_executor_cells"] == 0
    stage_rows = [f'First pilot & {stages[0]["actual_requests"]} & {failed["gate"]["valid_role_responses"]}/{failed["gate"]["scheduled_role_responses"]} & --- & 0 + {failed["scheduled_executor_cells"]}',
                  f'Repaired pilot & {stages[1]["actual_requests"]} & {data["pilot_gate"]["valid_role_responses"]}/108 & {pilot["task_correct"]}/{pilot["scheduled"]} & {pilot["invalid"]} + {pilot["missing"]}',
                  f'Frozen main & {stages[2]["actual_requests"]} & {main["valid_response"]+data["main_valid_summaries"]}/{data["main_scheduled_roles"]} & {main["task_correct"]}/{main["scheduled"]} & {main["invalid"]} + {main["missing"]}']
    out += [r"\newcommand{\StageRows}{", *[s + r" \\" for s in stage_rows], "}"]
    for label, ex in zip(("One", "Two"), data["examples"]):
        for name, field in (("ID", "scenario_id"), ("Answer", "gold_answer"), ("Record", "record_paragraph_verbatim")):
            out.append(r"\newcommand{\Example" + label + name + "}{" + tex(ex[field]) + "}")
    out += [r"\newcommand{\ExampleOneSummary}{" + tex(data["examples"][0]["summary_excerpt_verbatim"]) + "}"]
    return "\n".join(out) + "\n"


def generated(data):
    # Render literal backtick glyphs explicitly; the cached typewriter encoding
    # otherwise displays them as curly quotation marks. This is typography only:
    # parse_actions above receives the complete original fenced response.
    response = data["examples"][1]["response_verbatim"]
    lines = response.splitlines()
    assert lines[0] == "```json" and lines[-1] == "```"
    # T1 slot 0 is the literal grave glyph in the already used Latin Modern font.
    fence = r"{\fontencoding{T1}\ttfamily\char0\char0\char0"
    formatted = fence + " json}\\par\n\\begin{verbatim}\n" + "\n".join(lines[1:-1]) + "\n\\end{verbatim}\n" + fence + "}\\par\n"
    return {"evidence.tex": render(data),
            "source-map.json": json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
            "format-example.tex": formatted}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--render", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = derive()
    for name, text in generated(data).items():
        target = HERE / name
        if args.render:
            target.write_text(text, encoding="utf-8")
        elif target.read_text(encoding="utf-8") != text:
            raise ValueError("reader artifact differs from saved evidence: " + name)
    print(canonical({"reader_evidence_passed": True, "mode": "render" if args.render else "check",
                     "main": data["main"], "main_clusters": data["main_clusters"],
                     "examples_checked": len(data["examples"]), "source_files": len(data["source_files_sha256"]),
                     "new_api_requests": 0}))


if __name__ == "__main__":
    main()