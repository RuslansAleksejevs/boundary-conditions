"""Prospective acquisition, separate live audit and empirical freeze.

Offline auditors remain offline-only. Shared execution/scoring is reused only
after this module checks actual HTTP receipts and the durable budget journal.
"""

import os
import random
import time
import math
import platform
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from .adapters import parse_review, parse_translation
from .analysis import analyze
from .dataset import audit_dataset, make_dataset, make_exclusions
from .live_budget import BudgetLedger, BudgetStop, ledger_state, money
from .live_http import (OpenRouterHTTP, budget_configuration_hash, interpret_receipt,
                        payload_for, upper_cost, validate_configuration, visible_response)
from .logic import SchemaError, canonical, digest, keys, strict_json
from .pipeline import (audit_content, collect_records, pilot_statistics, timestamp)
from .prompts import prompt_spec
from .records import code_hashes, git_revision, read_json as read_record_json, write_new
from .vector import signature


ENGINEERING_SEEDS = (6006, 6007, *range(6100, 6110))
LIVE_KIND = "live_model_acquisition"
FIXTURE_KIND = "live_transport_fixture"
SCHEDULE = {"pilot-v1": 52, "pilot-v2": 52, "main": 260,
            "max_extra_technical_attempts": 15, "max_total_attempts": 379}


def read_json(path):
    # Visible SSE events make live acquisition records larger than offline tapes.
    # This is a bounded local-record limit, never a provider-response byte cap.
    return read_record_json(path, max_bytes=512_000_000)


def known_transport_fixture_datasets():
    """The two inspected test recipes, not recursively generated new fixtures.

    Library tests prepare their fixed 12-source bundle. The acquisition CLI also
    excludes that exact bundle and the two-source exclusion test's bundle.
    """
    legacy = [make_dataset(s) for s in ENGINEERING_SEEDS]
    return [make_dataset(2026110806, exclusions=make_exclusions(sources))
            for sources in (legacy[:2], legacy)]


def time_value(value):
    try:
        result = datetime.fromisoformat(value)
        if result.tzinfo is None:
            raise ValueError("naive timestamp")
        return result
    except (TypeError, ValueError) as error:
        raise SchemaError("timezone-aware ISO timestamp required") from error


def validate_manifest(dataset, manifest):
    keys(manifest, ("version", "kind", "created_at", "python_version", "code_revision", "code_hashes",
                    "dataset_hash", "exclusion_hash", "configuration", "configuration_hash",
                    "budget_configuration_hash", "prompt_spec", "orders", "schedule",
                    "worst_case_attempt_usd", "worst_case_379_attempts_usd", "full_schedule_reservation_fits_quota",
                    "ground_truth_audit", "revision"))
    audit = audit_dataset(dataset)
    config = validate_configuration(manifest["configuration"])
    time_value(manifest["created_at"])
    if (type(manifest["version"]) is not int or manifest["version"] != 1
            or manifest["kind"] != "prospective_live_campaign" or dataset["version"] != 2
            or manifest["dataset_hash"] != digest(dataset)
            or manifest["exclusion_hash"] != dataset["exclusions"]["hash"]
            or manifest["configuration_hash"] != digest(config)
            or manifest["budget_configuration_hash"] != budget_configuration_hash(config)
            or manifest["orders"] != frozen_orders(dataset)
            or manifest["schedule"] != SCHEDULE or manifest["prompt_spec"] != prompt_spec()
            or manifest["ground_truth_audit"] != audit
            or money(manifest["worst_case_attempt_usd"]) != upper_cost(config)
            or money(manifest["worst_case_379_attempts_usd"]) != 379 * upper_cost(config)
            or manifest["full_schedule_reservation_fits_quota"] is not (379 * upper_cost(config) <= money("20"))):
        raise SchemaError("live campaign binding mismatch")
    hashes = manifest["code_hashes"]
    if (type(hashes) is not dict or not hashes
            or any(type(k) is not str or type(v) is not str or len(v) != 64 for k, v in hashes.items())):
        raise SchemaError("invalid code inventory")
    if manifest["revision"] is not None:
        keys(manifest["revision"], ("prior_manifest_hash", "prior_pilot_hash", "description", "authorization_reference"))
        if any(type(value) is not str or not value.strip() for value in manifest["revision"].values()):
            raise SchemaError("incomplete genuine interface correction record")
    return manifest


def frozen_orders(dataset):
    result = {}
    for split, cases in dataset["splits"].items():
        ordered = list(cases)
        if split == "dev":
            # The first clean natural tasks are also the connection check. They
            # remain ordinary planned pilot calls, not an extra smoke batch.
            first = [next(c for c in cases if c["group"] == "natural" and c["family"] == label)
                     for label in ("SAFE", "UNSAFE")]
            ordered = first + [c for c in cases if c not in first]
        rng = random.Random(dataset["seed"] + (19 if split == "dev" else 71))
        conditions = {}
        for case in ordered:
            if case["group"] != "natural":
                arms = ["B", "N", "S"]
                rng.shuffle(arms)
                conditions[case["id"]] = arms
        result[split] = {"cases": [c["id"] for c in ordered], "conditions": conditions}
    return result


def scheduled_ids(dataset, manifest, split):
    by_id = {case["id"]: case for case in dataset["splits"][split]}
    result = []
    order = manifest["orders"][split]
    for case_id in order["cases"]:
        if by_id[case_id]["group"] == "natural":
            result.extend((case_id + ":translator:-", case_id + ":reviewer:B"))
        else:
            result.extend(case_id + ":reviewer:" + condition for condition in order["conditions"][case_id])
    return result


def prepare_live(path, config, seed, extra_excluded_datasets=()):
    validate_configuration(config)
    path = Path(path)
    if path.exists():
        raise FileExistsError("live campaign already exists; preserve it")
    excluded = [make_dataset(s) for s in ENGINEERING_SEEDS] + list(extra_excluded_datasets)
    exclusions = make_exclusions(excluded)
    dataset = make_dataset(seed, exclusions=exclusions)
    manifest = {"version": 1, "kind": "prospective_live_campaign", "created_at": timestamp(),
                "python_version": platform.python_version(),
                "code_revision": git_revision(), "code_hashes": code_hashes(),
                "dataset_hash": digest(dataset), "exclusion_hash": exclusions["hash"],
                "configuration": config, "configuration_hash": digest(config),
                "budget_configuration_hash": budget_configuration_hash(config),
                "prompt_spec": prompt_spec(), "orders": frozen_orders(dataset),
                "schedule": dict(SCHEDULE),
                "worst_case_attempt_usd": str(upper_cost(config)),
                "worst_case_379_attempts_usd": str(379 * upper_cost(config)),
                "full_schedule_reservation_fits_quota": 379 * upper_cost(config) <= money("20"),
                "ground_truth_audit": audit_dataset(dataset), "revision": None}
    path.mkdir(parents=True, mode=0o700)
    write_new(path / "dataset.json", dataset)
    write_new(path / "manifest.json", manifest)
    return manifest


def load_live(path, manifest_name="manifest.json", check_code=True):
    path = Path(path)
    dataset, manifest = read_json(path / "dataset.json"), read_json(path / manifest_name)
    validate_manifest(dataset, manifest)
    if check_code and manifest["code_hashes"] != code_hashes():
        raise SchemaError("live source/tests changed; no acquisition under stale manifest")
    return dataset, manifest


def validate_go(go, manifest, stage=None):
    keys(go, ("version", "decision", "study", "configuration_hash", "code_hashes_hash",
              "manifest_hash", "allowed_stages", "approved_at", "authorization_reference", "quota_usd"))
    time_value(go["approved_at"])
    allowed = go["allowed_stages"]
    if (type(go["version"]) is not int or go["version"] != 1 or go["decision"] != "GO"
            or go["study"] != "wrong-goal-proof" or money(go["quota_usd"]) != money("20")
            or go["configuration_hash"] != manifest["configuration_hash"]
            or go["manifest_hash"] != digest(manifest)
            or go["code_hashes_hash"] != digest(manifest["code_hashes"])
            or type(allowed) is not list or any(type(s) is not str for s in allowed)
            or len(set(allowed)) != len(allowed) or not set(allowed) <= {"pilot-v1", "pilot-v2", "main"}
            or (stage is not None and stage not in allowed)
            or type(go["authorization_reference"]) is not str or not go["authorization_reference"].strip()):
        raise SchemaError("coordinator GO does not bind this manifest, configuration, code, and stage")


def response_record(request, variables, interpreted, started_at, elapsed, invoked=True):
    record = {"request": request, "status": interpreted["status"],
              "response_text": interpreted["text"], "usage": interpreted["usage"],
              "parsed": None, "error": interpreted["error"], "adapter_invoked": invoked,
              "started_at": started_at, "latency_seconds": elapsed}
    if interpreted["status"] == "response":
        try:
            parser = parse_translation if request["role"] == "translator" else parse_review
            record["parsed"] = parser(interpreted["text"], variables)
            record["status"] = "completed"
        except SchemaError as error:
            record.update(status="schema_error", error=str(error))
    return record


class Acquirer:
    def __init__(self, config, ledger, transport, stage, emit, prior_provider_ids=()):
        self.config, self.ledger, self.transport, self.stage = config, ledger, transport, stage
        self.emit, self.receipts, self.halt_reason = emit, [], None
        self.consecutive_transport_failures = 0
        self.provider_ids = set(prior_provider_ids)
        self.configuration = {"kind": LIVE_KIND if transport.kind == "official_openrouter_http" else FIXTURE_KIND,
                              "transport": transport.kind, "configuration": config}

    def record_call(self, request, variables):
        started, clock = timestamp(), time.perf_counter()
        empty = {"status": "not_attempted", "text": None, "usage": None, "error": self.halt_reason}
        if self.halt_reason is not None:
            return response_record(request, variables, empty, started, 0.0, invoked=False)
        try:
            body = payload_for(request, self.config)
        except SchemaError as error:
            self.halt_reason = str(error)
            empty["error"] = self.halt_reason
            return response_record(request, variables, empty, started, 0.0, invoked=False)
        retry_of, interpreted = None, None
        for index in range(2):
            try:
                aid = self.ledger.reserve(request["id"], self.stage, digest(body, "wgp-http-request-v1"),
                                          upper_cost(self.config), retry_of=retry_of)
            except BudgetStop as error:
                self.halt_reason = str(error)
                if interpreted is None:
                    empty.update(status="budget_blocked", error=self.halt_reason)
                    return response_record(request, variables, empty, started, 0.0, invoked=False)
                break
            self.emit({"event": "http_intent", "attempt_id": aid, "request_id": request["id"],
                       "stage": self.stage, "payload": body, "timestamp": timestamp()})
            send_started, send_clock = timestamp(), time.perf_counter()
            try:
                result = self.transport.send(body)
            except Exception as error:
                # An uncertain client-side failure may already have reached the
                # provider. Retain the entire reservation and stop; do not retry
                # arbitrary permission errors or programming exceptions.
                result = {"started_at": send_started, "finished_at": timestamp(), "latency_seconds": time.perf_counter() - send_clock,
                          "http_status": None, "headers": {}, "response": None,
                          "stream": None,
                          "transport_error": "client_exception_" + type(error).__name__,
                          "retryable_transport": False}
            receipt = {"attempt_id": aid, "logical_id": request["id"], "stage": self.stage,
                       "transport_kind": self.transport.kind, "prompt_hash": request["prompt_hash"],
                       "payload": body, "payload_hash": digest(body, "wgp-http-request-v1"), **result}
            self.receipts.append(receipt)
            self.emit({"event": "http_receipt", "record": receipt})
            interpreted = interpret_receipt(receipt, self.config)
            self.ledger.settle(aid, interpreted["ledger_charge_usd"], interpreted["retryable"], receipt)
            pid = interpreted["provider_request_id"]
            if pid is not None:
                if pid in self.provider_ids:
                    self.halt_reason = "duplicate provider acquisition ID; stop for reconciliation"
                self.provider_ids.add(pid)
            if interpreted["fatal"]:
                self.halt_reason = interpreted["error"]
            if (index == 0 and interpreted["retryable"] and self.halt_reason is None
                    and self.ledger.state()["retries"] < 15):
                retry_of = aid
                continue
            break
        if interpreted["status"] == "transport_error":
            self.consecutive_transport_failures += 1
            if self.consecutive_transport_failures >= 3:
                self.halt_reason = "three consecutive failed logical transports; stop for diagnosis"
        else:
            self.consecutive_transport_failures = 0
        return response_record(request, variables, interpreted, started, time.perf_counter() - clock)


def audit_live(dataset, manifest, run, allow_fixture=False):
    validate_manifest(dataset, manifest)
    keys(run, ("version", "split", "dataset_hash", "manifest_hash", "adapter", "started_at",
               "scheduled_calls", "calls", "outcomes", "finished_at", "elapsed_seconds",
               "stage", "new_model_calls", "receipts", "ledger_events", "go", "halt_reason"))
    validate_go(run["go"], manifest, run["stage"])
    config = validate_configuration(manifest["configuration"])
    expected_kind = LIVE_KIND
    if allow_fixture and run["adapter"]["kind"] == FIXTURE_KIND:
        expected_kind = FIXTURE_KIND
    if (run["adapter"]["kind"] != expected_kind or run["adapter"]["configuration"] != config
            or run["manifest_hash"] != digest(manifest) or run["dataset_hash"] != digest(dataset)
            or run["stage"] not in ("pilot-v1", "pilot-v2", "main")
            or run["split"] != ("holdout" if run["stage"] == "main" else "dev")):
        raise SchemaError("live acquisition identity mismatch")
    if [call["request"]["id"] for call in run["calls"]] != scheduled_ids(dataset, manifest, run["split"]):
        raise SchemaError("role order differs from the prospectively fixed schedule")
    state = ledger_state(run["ledger_events"], manifest["budget_configuration_hash"])
    by_request, seen_ids, provider_ids = {}, set(), set()
    for receipt in run["receipts"]:
        keys(receipt, ("attempt_id", "logical_id", "stage", "transport_kind", "prompt_hash", "payload",
                       "payload_hash", "started_at", "finished_at", "latency_seconds", "http_status",
                       "headers", "response", "stream", "transport_error", "retryable_transport"))
        if (not time_value(run["go"]["approved_at"]) <= time_value(receipt["started_at"]) <= time_value(receipt["finished_at"])
                or type(receipt["latency_seconds"]) not in (int, float)
                or not math.isfinite(receipt["latency_seconds"]) or receipt["latency_seconds"] < 0
                or type(receipt["headers"]) is not dict
                or (receipt["http_status"] is not None and type(receipt["http_status"]) is not int)
                or (receipt["transport_error"] is not None and type(receipt["transport_error"]) is not str)
                or receipt["response"] != visible_response(receipt["response"])
                or receipt["stream"] != visible_response(receipt["stream"])):
            raise SchemaError("invalid acquisition timing/schema or retained reasoning text")
        aid = receipt["attempt_id"]
        reservation, settlement = state["reservations"].get(aid), state["settlements"].get(aid)
        if aid in seen_ids or reservation is None or settlement is None:
            raise SchemaError("missing/duplicate acquisition reservation or settlement")
        seen_ids.add(aid)
        if (receipt["stage"] != run["stage"] or reservation["stage"] != run["stage"]
                or receipt["logical_id"] != reservation["logical_id"]
                or receipt["transport_kind"] != run["adapter"]["transport"]
                or (expected_kind == LIVE_KIND and receipt["transport_kind"] != "official_openrouter_http")
                or receipt["payload_hash"] != digest(receipt["payload"], "wgp-http-request-v1")
                or reservation["request_hash"] != receipt["payload_hash"]
                or settlement["receipt_hash"] != digest(receipt, "wgp-receipt-v1")
                or money(reservation["reserve_usd"]) != upper_cost(config)):
            raise SchemaError("acquisition/reservation binding mismatch")
        interpreted = interpret_receipt(receipt, config)
        charge = interpreted["ledger_charge_usd"]
        expected_cost = None if charge is None else str(money(charge))
        if settlement["confirmed_charge_usd"] != expected_cost or settlement["retryable"] != interpreted["retryable"]:
            raise SchemaError("settlement does not match provider receipt")
        pid = interpreted["provider_request_id"]
        if pid is not None:
            if pid in provider_ids:
                raise SchemaError("duplicate provider acquisition ID")
            provider_ids.add(pid)
        by_request.setdefault(receipt["logical_id"], []).append(receipt)
    stage_reservations = {aid for aid, r in state["reservations"].items() if r["stage"] == run["stage"]}
    if seen_ids != stage_reservations:
        raise SchemaError("incomplete acquisition log: stage reservations and receipts differ")
    if [r["attempt_id"] for r in run["receipts"]] != [aid for aid, r in state["reservations"].items()
                                                    if r["stage"] == run["stage"]]:
        raise SchemaError("receipt order differs from durable reservation order")
    if (type(run["new_model_calls"]) is not int
            or run["new_model_calls"] != (len(run["receipts"]) if expected_kind == LIVE_KIND else 0)):
        raise SchemaError("physical model call count mismatch")
    records = {c["request"]["id"]: c for c in run["calls"]}
    for request_id, receipts in by_request.items():
        record = records.get(request_id)
        if record is None:
            raise SchemaError("receipt has no scheduled role")
        for receipt in receipts:
            if (receipt["payload"] != payload_for(record["request"], config)
                    or receipt["prompt_hash"] != record["request"]["prompt_hash"]):
                raise SchemaError("raw HTTP request differs from scheduled prompt")
        # The latest technical attempt is the sole retained model answer. There is
        # no semantic retry or best-of-N selection in the ledger policy.
        interpreted = interpret_receipt(receipts[-1], config)
        case_id = request_id.split(":", 1)[0]
        case = next(c for c in dataset["splits"][run["split"]] if c["id"] == case_id)
        expected = response_record(record["request"], case["original"]["variables"], interpreted,
                                   record["started_at"], record["latency_seconds"])
        if canonical(expected) != canonical(record):
            raise SchemaError("role outcome does not match raw provider acquisition")
    for record in run["calls"]:
        if record["adapter_invoked"] and record["request"]["id"] not in by_request:
            raise SchemaError("claimed invocation lacks an acquisition receipt")
        if record["status"] in ("not_attempted", "budget_blocked") and not run["halt_reason"]:
            raise SchemaError("unattempted scheduled role lacks an explicit stop reason")
    math_audit = audit_content(dataset, run, live=True)
    return {**math_audit, "mode": expected_kind, "new_model_calls": run["new_model_calls"],
            "physical_attempts": len(run["receipts"]), "ledger": {
                k: state[k] for k in ("attempts", "retries", "committed_usd", "settled_conservative_usd", "unknown_charges", "pricing_overrun")},
            "provenance_authenticated": False}


def revised_pilot_manifest(path, description, authorization_reference):
    """One transport-only correction. Never change tasks, prompts, or economics.

    A semantic/prompt revision needs an explicit separately reviewed protocol;
    this bounded command deliberately does not implement prompt search.
    """
    path = Path(path)
    dataset, prior = load_live(path, check_code=False)
    if (path / "freeze.json").exists() or (path / "main").exists():
        raise SchemaError("cannot revise after freeze/evaluation")
    pilot = read_json(path / "pilot-v1" / "run.json")
    gate = live_pilot_gate(dataset, prior, pilot)
    if gate["passed"]:
        raise SchemaError("passing pilot cannot be repeated")
    if not gate["actual_pilot_holdout_separation"]["valid"]:
        raise SchemaError("pilot/main collision cannot justify an interface-correction repeat")
    if prior["code_hashes"] == code_hashes():
        raise SchemaError("no actual interface implementation correction to freeze")
    manifest = {**prior, "created_at": timestamp(), "code_revision": git_revision(), "code_hashes": code_hashes(),
                "revision": {"prior_manifest_hash": digest(prior), "prior_pilot_hash": digest(pilot),
                             "description": description, "authorization_reference": authorization_reference}}
    validate_manifest(dataset, manifest)
    write_new(path / "manifest-v2.json", manifest)
    return manifest


def run_live_stage(path, stage, go, api_key=None, transport=None):
    path = Path(path)
    if stage not in ("pilot-v1", "pilot-v2", "main"):
        raise SchemaError("unknown live stage")
    manifest_name = "manifest-v2.json" if stage == "pilot-v2" else "manifest.json"
    if stage == "main":
        frozen = read_json(path / "freeze.json")
        manifest_name = frozen["manifest_name"]
    dataset, manifest = load_live(path, manifest_name)
    validate_go(go, manifest, stage)
    previous = None
    if transport is None:
        sources = {s["dataset_hash"] for s in dataset["exclusions"]["sources"]}
        required = {digest(make_dataset(s)) for s in ENGINEERING_SEEDS}
        required.update(digest(d) for d in known_transport_fixture_datasets())
        if not required <= sources:
            raise SchemaError("real acquisition must exclude all inspected engineering and transport-test bundles")
    if stage == "pilot-v2" and not manifest["revision"]:
        raise SchemaError("second pilot requires documented genuine interface correction")
    if stage == "pilot-v2":
        _, prior = load_live(path, check_code=False)
        previous = read_json(path / "pilot-v1" / "run.json")
        first_gate = live_pilot_gate(dataset, prior, previous)
        if (first_gate["passed"] or not first_gate["actual_pilot_holdout_separation"]["valid"]
                or manifest["revision"]["prior_pilot_hash"] != digest(previous)
                or manifest["revision"]["prior_manifest_hash"] != digest(prior)):
            raise SchemaError("revision does not bind the actual failed first pilot")
    if stage == "main":
        if (frozen["manifest_hash"] != digest(manifest) or frozen["code_hashes"] != code_hashes()
                or not frozen["pilot_gate"]["passed"] or frozen["configuration_hash"] != manifest["configuration_hash"]):
            raise SchemaError("empirical freeze mismatch")
        pilot_stage = "pilot-v2" if manifest_name == "manifest-v2.json" else "pilot-v1"
        pilot = read_json(path / pilot_stage / "run.json")
        earlier_pilots = ([(load_live(path, check_code=False)[1], read_json(path / "pilot-v1" / "run.json"))]
                          if pilot_stage == "pilot-v2" else [])
        gate = live_pilot_gate(dataset, manifest, pilot, previous_pilots=earlier_pilots)
        if digest(pilot) != frozen["pilot_run_hash"] or canonical(gate) != canonical(frozen["pilot_gate"]):
            raise SchemaError("freeze does not bind the actual passing pilot")
        if (frozen["status"] != "prospective_empirical_freeze"
                or frozen["dataset_hash"] != digest(dataset) or frozen["exclusion_hash"] != manifest["exclusion_hash"]
                or not time_value(pilot["finished_at"]) <= time_value(frozen["created_at"]) <= time_value(timestamp())):
            raise SchemaError("invalid or nonprospective empirical freeze")
        previous = pilot
    config = manifest["configuration"]
    transport = transport or OpenRouterHTTP(api_key, config["timeout_seconds"])
    split = "holdout" if stage == "main" else "dev"
    with BudgetLedger(path / "budget.jsonl", manifest["budget_configuration_hash"]) as ledger:
        if canonical(ledger.events) != canonical(previous["ledger_events"] if previous else []):
            raise SchemaError("budget ledger differs from prior completed stage; stop for reconciliation")
        directory = path / stage
        directory.mkdir(mode=0o700, exist_ok=False)
        with (directory / "events.jsonl").open("x", encoding="utf-8") as stream:
            def emit(event):
                stream.write(canonical(event) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            prior_ids = ([interpret_receipt(r, config)["provider_request_id"] for r in previous["receipts"]]
                         if previous else [])
            if stage == "main" and manifest["revision"] is not None:
                prior_ids.extend(interpret_receipt(r, config)["provider_request_id"]
                                 for r in read_json(path / "pilot-v1" / "run.json")["receipts"])
            acquirer = Acquirer(config, ledger, transport, stage, emit, [p for p in prior_ids if p is not None])
            orders = manifest["orders"][split]
            run = collect_records(dataset, split, acquirer, digest(manifest), emit,
                                  call_function=lambda adapter, request, variables: adapter.record_call(request, variables),
                                  case_order=orders["cases"], condition_order=orders["conditions"])
            run.update(stage=stage, receipts=acquirer.receipts, ledger_events=ledger.events,
                       go=go, halt_reason=acquirer.halt_reason,
                       new_model_calls=len(acquirer.receipts) if transport.kind == "official_openrouter_http" else 0)
            audit_live(dataset, manifest, run, allow_fixture=transport.kind != "official_openrouter_http")
            emit({"event": "run_end", "run_hash": digest(run), "timestamp": timestamp()})
    write_new(directory / "run.json", run)
    return run


def live_pilot_gate(dataset, manifest, run, previous_pilots=()):
    result = audit_live(dataset, manifest, run)
    if run["stage"] not in ("pilot-v1", "pilot-v2") or run["split"] != "dev":
        raise SchemaError("evaluation cannot qualify as a pilot")
    if len(previous_pilots) != (1 if run["stage"] == "pilot-v2" else 0):
        raise SchemaError("gate must include every preserved prior pilot")
    for prior_manifest, prior_run in previous_pilots:
        first_gate = live_pilot_gate(dataset, prior_manifest, prior_run)
        if (prior_run["stage"] != "pilot-v1" or first_gate["passed"]
                or not first_gate["actual_pilot_holdout_separation"]["valid"]
                or manifest["revision"] is None
                or manifest["revision"]["prior_manifest_hash"] != digest(prior_manifest)
                or manifest["revision"]["prior_pilot_hash"] != digest(prior_run)
                or run["ledger_events"][:len(prior_run["ledger_events"])] != prior_run["ledger_events"]):
            raise SchemaError("corrected-pilot gate does not bind its failed, nonoverlapping first pilot")
    gate = pilot_statistics(run, "prospective live-model pilot")
    gate["actual_pilot_holdout_separation"] = actual_pilot_separation(dataset, run,
        previous_pilots=[prior_run for _, prior_run in previous_pilots])
    gate["main_budget_projection"] = main_budget_projection(manifest["configuration"], run, result["ledger"])
    gate["passed"] = (gate["passed"] and run["halt_reason"] is None
                      and not result["ledger"]["pricing_overrun"]
                      and gate["actual_pilot_holdout_separation"]["valid"]
                      and money(result["ledger"]["committed_usd"]) <= money("20"))
    return gate


def main_budget_projection(config, pilot, ledger):
    """Prospective operational projection, not a guarantee or an outcome filter.

    The fixed main sample is not shortened. The coordinator inspects this record
    before main; the actual wallet independently guards every later dispatch.
    """
    charges = [interpret_receipt(r, config)["ledger_charge_usd"] for r in pilot["receipts"]]
    reserved = upper_cost(config)
    amounts = [reserved if charge is None else money(charge) for charge in charges]
    remaining = 260 + max(0, 15 - ledger["retries"])
    committed = money(ledger["committed_usd"])
    mean = sum(amounts, Decimal(0)) / len(amounts) if amounts else None
    maximum = max(amounts) if amounts else None
    return {"planned_main_logical_calls": 260, "maximum_remaining_main_attempts": remaining,
            "pilot_physical_attempts": len(charges), "unknown_pilot_costs": sum(c is None for c in charges),
            "already_charged_or_reserved_usd": str(committed),
            "mean_with_unknown_costs_at_full_reserve_usd": None if mean is None else str(mean),
            "observed_max_with_unknown_costs_at_full_reserve_usd": None if maximum is None else str(maximum),
            "projected_campaign_mean_usd": None if mean is None else str(committed + remaining * mean),
            "projected_campaign_observed_max_usd": None if maximum is None else str(committed + remaining * maximum),
            "full_context_worst_case_campaign_usd": str(committed + remaining * reserved),
            "next_full_reservation_fits_quota": committed + reserved <= money("20"),
            "projection_is_a_guaranteed_bound": False,
            "policy": "No adaptive sample shrink; a hard-wallet stop leaves scheduled outcomes unassessed."}


def actual_pilot_separation(dataset, pilot, previous_pilots=()):
    """Include actual translator outputs, not only the generator's reference AST.

    A collision blocks the frozen main set. No post-outcome resampling is built
    into acquisition; resolution requires an explicitly reviewed protocol change.
    """
    observed = {signature(o["candidate"]) for run in [*previous_pilots, pilot]
                for o in run["outcomes"] if o["candidate"] is not None}
    holdout = {signature(c[name]) for c in dataset["splits"]["holdout"]
               for name in ("original", "candidate") if c[name] is not None}
    overlap = observed & holdout
    return {"valid": not overlap, "preserved_pilots_checked": 1 + len(previous_pilots),
            "distinct_observed_candidate_functions": len(observed),
            "overlapping_functions": len(overlap),
            "observed_candidate_function_hash": digest(sorted(observed), "wgp-observed-pilot-functions-v1")}


def freeze_live(path, pilot_stage="pilot-v1"):
    path = Path(path)
    if pilot_stage not in ("pilot-v1", "pilot-v2"):
        raise SchemaError("freeze requires a pilot, not evaluation")
    name = "manifest-v2.json" if pilot_stage == "pilot-v2" else "manifest.json"
    dataset, manifest = load_live(path, name)
    run = read_json(path / pilot_stage / "run.json")
    previous_pilots = ([(load_live(path, check_code=False)[1], read_json(path / "pilot-v1" / "run.json"))]
                       if pilot_stage == "pilot-v2" else [])
    gate = live_pilot_gate(dataset, manifest, run, previous_pilots=previous_pilots)
    if not gate["passed"]:
        raise SchemaError("live pilot gate failed; do not run main")
    frozen = {"version": 1, "status": "prospective_empirical_freeze", "created_at": timestamp(),
              "manifest_name": name, "manifest_hash": digest(manifest), "pilot_run_hash": digest(run),
              "pilot_gate": gate, "configuration_hash": manifest["configuration_hash"],
              "code_hashes": code_hashes(), "dataset_hash": digest(dataset),
              "exclusion_hash": manifest["exclusion_hash"], "not_public_preregistration": True}
    write_new(path / "freeze.json", frozen)
    return frozen


def audit_campaign(path, allow_fixture=False):
    """Check every stage against the same financial history and actual pilot.

    Partial/crashed stages fail closed. Their journal and unreleased reservation
    remain on disk for diagnosis; this command never repairs or resumes them.
    """
    path = Path(path)
    previous, stage_reports, provider_ids = [], {}, set()
    runs, manifests = {}, {}
    for stage in ("pilot-v1", "pilot-v2", "main"):
        if not (path / stage).exists():
            continue
        if stage == "pilot-v2" and "pilot-v1" not in runs:
            raise SchemaError("second pilot without the first preserved pilot")
        if stage == "main" and not runs:
            raise SchemaError("evaluation without a preserved pilot")
        name = (read_json(path / "freeze.json")["manifest_name"] if stage == "main"
                else "manifest-v2.json" if stage == "pilot-v2" else "manifest.json")
        dataset, manifest = load_live(path, name, check_code=False)
        run = read_json(path / stage / "run.json")
        report = audit_live(dataset, manifest, run, allow_fixture=allow_fixture)
        events = run["ledger_events"]
        if events[:len(previous)] != previous:
            raise SchemaError("campaign ledger prefix changed between stages")
        if any(event["action"] == "reserve" and event["data"]["stage"] != stage
               for event in events[len(previous):]):
            raise SchemaError("unlogged or foreign-stage reservation in campaign prefix")
        if stage == "pilot-v2":
            revision = manifest["revision"]
            first_gate = live_pilot_gate(dataset, manifests["pilot-v1"], runs["pilot-v1"])
            if (revision is None or revision["prior_manifest_hash"] != digest(manifests["pilot-v1"])
                    or revision["prior_pilot_hash"] != digest(runs["pilot-v1"])
                    or first_gate["passed"] or not first_gate["actual_pilot_holdout_separation"]["valid"]):
                raise SchemaError("unjustified or unbound repeated pilot")
        if stage == "main":
            frozen = read_json(path / "freeze.json")
            pilot_stage = "pilot-v2" if name == "manifest-v2.json" else "pilot-v1"
            pilot = runs[pilot_stage]
            previous_pilots = ([(manifests["pilot-v1"], runs["pilot-v1"])] if pilot_stage == "pilot-v2" else [])
            gate = live_pilot_gate(dataset, manifest, pilot, previous_pilots=previous_pilots)
            if (not gate["passed"] or frozen["pilot_gate"] != gate
                    or frozen["pilot_run_hash"] != digest(pilot)
                    or frozen["manifest_hash"] != digest(manifest)
                    or not time_value(pilot["finished_at"]) <= time_value(frozen["created_at"]) <= time_value(run["started_at"])):
                raise SchemaError("evaluation is not downstream of the actual frozen passing pilot")
        for receipt in run["receipts"]:
            pid = interpret_receipt(receipt, manifest["configuration"])["provider_request_id"]
            if pid is not None:
                if pid in provider_ids:
                    raise SchemaError("provider acquisition ID repeated across campaign stages")
                provider_ids.add(pid)
        previous, runs[stage], manifests[stage], stage_reports[stage] = events, run, manifest, report
    if not runs:
        raise SchemaError("no completed acquisition stage exists")
    raw = (path / "budget.jsonl").read_text(encoding="utf-8")
    if (not raw.endswith("\n") or [strict_json(line) for line in raw.splitlines()] != previous):
        raise SchemaError("current wallet differs from the last completed acquisition")
    return {"valid": True, "stages": stage_reports,
            "new_model_calls": sum(run["new_model_calls"] for run in runs.values()),
            "physical_attempts": sum(len(run["receipts"]) for run in runs.values()),
            "provenance_authenticated": False}


def analyze_live(dataset, manifest, run):
    audit = audit_live(dataset, manifest, run)
    report = analyze(run)
    interpretations = [interpret_receipt(r, manifest["configuration"]) for r in run["receipts"]]
    usage = {}
    for field in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens", "cost_usd"):
        known = [r["usage"][field] for r in interpretations if r["usage"][field] is not None]
        usage[field] = {"known_sum": sum(known), "known_attempts": len(known),
                        "physical_attempts": len(interpretations),
                        "total": sum(known) if len(known) == len(interpretations) else None}
    report.update(mode=LIVE_KIND, acquisition_audit=audit, usage=usage,
                  source_run_hash=digest(run), manifest_hash=digest(manifest), dataset_hash=digest(dataset),
                  configuration=manifest["configuration"],
                  physical_attempts=len(run["receipts"]),
                  provider_refusals=sum(c["status"] == "refused" for c in run["calls"]),
                  truncated_responses=sum(c["status"] == "truncated" for c in run["calls"]),
                  output_usage_above_requested_cap=sum(r["usage"]["output_tokens"] is not None
                      and r["usage"]["output_tokens"] > manifest["configuration"]["max_tokens"] for r in interpretations),
                  local_adapter_latency_seconds=sum(r["latency_seconds"] for r in run["receipts"]),
                  latency_note="Observed client-side HTTP latency including each technical attempt.",
                  interpretation="Actual acquired model answers under the frozen finite-contract protocol; "
                                 "receipt hashes are integrity checks, not cryptographic provider authentication.")
    return report