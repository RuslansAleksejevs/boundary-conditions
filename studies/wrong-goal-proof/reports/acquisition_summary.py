"""Reproduce operational accounting for an ended, fully audited campaign.

No model or network calls. This is presentation-only postprocessing, not new
scoring, acquisition authentication, or a substitute for account reconciliation.
"""

import argparse
from collections import Counter
from decimal import Decimal
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wgp.live import audit_campaign, load_live, read_json, time_value
from wgp.live_budget import ledger_state, money
from wgp.live_http import interpret_receipt
from wgp.logic import digest
from wgp.records import write_new


def known_total(values, *, monetary=False):
    """Unknown values affect the denominator and never become an exact total."""
    known = [value for value in values if value is not None]
    total = (sum((money(value) for value in known), Decimal(0)) if monetary
             else sum(known))
    if monetary:
        total = format(total, "f")
    return {"known_sum": total, "known_attempts": len(known),
            "unknown_attempts": len(values) - len(known),
            "physical_attempts": len(values),
            "total": total if len(known) == len(values) else None}


def receipt_timing(receipts):
    starts = [time_value(r["started_at"]) for r in receipts]
    latencies = [r["latency_seconds"] for r in receipts]
    gaps = [(right - left).total_seconds() for left, right in zip(starts, starts[1:])]
    prior_by_role, retries = {}, []
    for receipt in receipts:
        role = receipt["logical_id"]
        prior = prior_by_role.get(role)
        if prior is not None:
            retries.append({
                "logical_id": role,
                "prior_attempt_id": prior["attempt_id"],
                "retry_attempt_id": receipt["attempt_id"],
                "prior_http_status": prior["http_status"],
                "retry_http_status": receipt["http_status"],
                "identical_payload": receipt["payload"] == prior["payload"],
                "delay_after_prior_finish_seconds": (
                    time_value(receipt["started_at"]) - time_value(prior["finished_at"])
                ).total_seconds(),
            })
        prior_by_role[role] = receipt
    latency_sum = math.fsum(latencies)
    return {
        "minimum_attempt_start_spacing_seconds": min(gaps) if gaps else None,
        "latency_sum_seconds": latency_sum,
        "latency_mean_seconds": latency_sum / len(latencies) if latencies else None,
        "latency_max_seconds": max(latencies) if latencies else None,
        "technical_retries": len(retries), "retry_pairs": retries,
    }


def stage_summary(run, manifest, stage_audit):
    """Called only after campaign audit by the public command."""
    config = manifest["configuration"]
    receipts = run["receipts"]
    interpreted = [interpret_receipt(receipt, config) for receipt in receipts]
    # After validation, convert each parsed provider cost via Decimal(str(value))
    # rather than summing binary-float aggregates from analysis output. This does
    # not claim preservation of the original JSON wire spelling of a number.
    costs = [receipt["response"]["usage"]["cost"]
             if value["usage"]["cost_usd"] is not None else None
             for receipt, value in zip(receipts, interpreted)]
    state = ledger_state(run["ledger_events"], manifest["budget_configuration_hash"])
    reservations = {aid: reservation for aid, reservation in state["reservations"].items()
                    if reservation["stage"] == run["stage"]}
    settled, holds, unknown = Decimal(0), Decimal(0), 0
    unsettled, unsettled_reserve = 0, Decimal(0)
    for aid, reservation in reservations.items():
        charge = state["settlements"].get(aid, {}).get("confirmed_charge_usd")
        if charge is None:
            unknown += 1
            holds += money(reservation["reserve_usd"])
            if aid not in state["settlements"]:
                unsettled += 1
                unsettled_reserve += money(reservation["reserve_usd"])
        else:
            settled += money(charge)
    return {
        "stage": run["stage"], "source_run_hash": digest(run),
        "started_at": run["started_at"], "finished_at": run["finished_at"],
        "elapsed_seconds": run["elapsed_seconds"], "halt_reason": run["halt_reason"],
        "scheduled_roles": run["scheduled_calls"], "physical_attempts": len(receipts),
        "logical_role_statuses": dict(sorted(Counter(c["status"] for c in run["calls"]).items())),
        "http_statuses": dict(sorted(Counter(str(r["http_status"]) for r in receipts).items())),
        "reported_api_cost_usd": known_total(costs, monetary=True),
        "stage_wallet": {
            "settled_conservative_usd": format(settled, "f"),
            "unknown_charges": unknown, "unknown_holds_usd": format(holds, "f"),
            "unknown_settled_attempts": unknown - unsettled,
            "unknown_settled_holds_usd": format(holds - unsettled_reserve, "f"),
            "unsettled_reservations": unsettled,
            "unsettled_reserve_usd": format(unsettled_reserve, "f"),
            "committed_usd": format(settled + holds, "f"),
        },
        "cumulative_wallet_through_stage": stage_audit["ledger"],
        "usage": {field: known_total([value["usage"][field] for value in interpreted])
                  for field in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens")},
        "schema_failures": [{"role_id": c["request"]["id"], "role": c["request"]["role"],
                             "error": c["error"], "visible_characters": len(c["response_text"])}
                            for c in run["calls"] if c["status"] == "schema_error"],
        **receipt_timing(receipts),
    }


def campaign_summary(path):
    path = Path(path)
    if not (path / "main" / "run.json").is_file():
        raise ValueError("main must have ended before producing the final campaign summary")
    audit = audit_campaign(path)
    frozen = read_json(path / "freeze.json")
    load_live(path, frozen["manifest_name"], check_code=True)
    summaries = {}
    for stage, stage_audit in audit["stages"].items():
        manifest_name = (frozen["manifest_name"] if stage == "main" else
                         "manifest-v2.json" if stage == "pilot-v2" else "manifest.json")
        _, manifest = load_live(path, manifest_name, check_code=False)
        summaries[stage] = stage_summary(read_json(path / stage / "run.json"), manifest, stage_audit)
    costs = [summary["reported_api_cost_usd"] for summary in summaries.values()]
    known_sum = sum((money(cost["known_sum"]) for cost in costs), Decimal(0))
    unknown = sum(cost["unknown_attempts"] for cost in costs)
    return {
        "version": 1, "kind": "audited_campaign_operational_summary", "new_model_calls": 0,
        "full_campaign_audit_valid": audit["valid"], "source_inventory_matches": True,
        "provenance_authenticated": False, "stages": summaries,
        "campaign_reported_api_cost_usd": {
            "known_sum": format(known_sum, "f"),
            "known_attempts": sum(cost["known_attempts"] for cost in costs),
            "unknown_attempts": unknown,
            "physical_attempts": audit["physical_attempts"],
            "total": format(known_sum, "f") if unknown == 0 else None,
        },
        "notes": [
            "Reported API costs and conservative ledger settlements are distinct quantities.",
            "Unknown charges retain full reservations; neither unknown charges nor token usage are imputed zero.",
            "Stage wallets exclude earlier stages; cumulative wallets include them.",
            "Completed native audits require every reservation to have a settlement; unsettled reserves must therefore be zero here.",
            "Attempt-start and retry gaps are differences of recorded UTC timestamps; HTTP latency and stage elapsed time are client monotonic-clock durations.",
            "Timing and identical-request checks describe recorded receipts, not provider-signed attestations.",
            "HTTP status alone does not identify the cause of a provider error.",
            "Private account reconciliation and research-assistant session costs are outside this summary.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    summary = campaign_summary(args.campaign)
    write_new(args.out, summary)
    print(json.dumps({"new_model_calls": 0, "campaign_cost": summary["campaign_reported_api_cost_usd"],
                      "full_campaign_audit_valid": True}, indent=2))


if __name__ == "__main__":
    main()