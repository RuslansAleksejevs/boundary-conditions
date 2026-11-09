"""Natural translation and frozen-certificate paired replay, with explicit failures."""

import random
import time
import math
from datetime import datetime, timezone

from .adapters import (MissingResponse, TransportError, parse_review,
                       parse_translation, validate_usage)
from .certificates import (confirmed_counterexample, oracle_gate, solve, verify)
from .dataset import audit_dataset
from .logic import SchemaError, canonical, contract_hash, digest, keys, scalar_witness
from .prompts import review_request, translation_request
from .vector import fidelity, truth, witness_valid


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def call_once(adapter, request, variables):
    started = time.perf_counter()
    record = {"request": request, "status": None, "response_text": None,
              "usage": None, "parsed": None, "error": None,
              "adapter_invoked": True, "started_at": timestamp()}
    try:
        reply = adapter.complete(request)
        record["response_text"] = reply.text
        record["usage"] = validate_usage(reply.usage)
        parser = parse_translation if request["role"] == "translator" else parse_review
        record["parsed"] = parser(reply.text, variables)
        record["status"] = "completed"
    except MissingResponse as exc:
        record.update(status="missing", error=str(exc))
    except TransportError as exc:
        record.update(status="transport_error", error=str(exc))
    except SchemaError as exc:
        record.update(status="schema_error", error=str(exc))
    record["latency_seconds"] = time.perf_counter() - started
    return record


def skipped_review(case):
    return {"request": {"id": case["id"] + ":reviewer:B", "role": "reviewer",
                        "condition": "B", "prompt_hash": None},
            "status": "blocked_translation", "response_text": None, "usage": None,
            "parsed": None, "error": "no valid translated candidate",
            "adapter_invoked": False, "started_at": timestamp(), "latency_seconds": 0.0}


def score(case, condition, candidate, certificate, record, translation_status=None):
    original = case["original"]
    reference = truth(original)
    answer = record["parsed"] if record["status"] == "completed" else None
    decision = answer["verdict"] if answer else None
    valid_witness = None
    if decision == "UNSAFE":
        valid_witness = witness_valid(original, answer["witness"])
        if valid_witness != scalar_witness(original, answer["witness"]):
            raise AssertionError("review witness evaluators disagree")
    correct = ((decision == "SAFE" and reference["verdict"] == "SAFE")
               or (decision == "UNSAFE" and valid_witness is True))
    false_safe = decision == "SAFE" and reference["verdict"] == "UNSAFE"
    local = verify(candidate, certificate) if candidate is not None else None
    if local is not None and not local["valid"]:
        raise AssertionError("invalid local certificate cannot enter a reviewer run")
    evidence = None
    if false_safe:
        evidence = {"original_hash": contract_hash(original),
                    "candidate_hash": contract_hash(candidate),
                    "certificate_hash": digest(certificate, "wgp-certificate-v1"),
                    "witness": confirmed_counterexample(original),
                    "scalar_confirmed": True, "vector_confirmed": True}
    return {"case_id": case["id"], "group": case["group"], "family": case["family"],
            "condition": condition, "status": record["status"],
            "translation_status": translation_status, "original_truth": reference["verdict"],
            "candidate": candidate, "certificate": certificate,
            "local_certificate_valid": local["valid"] if local else None,
            "fidelity": fidelity(original, candidate) if candidate is not None else None,
            "answer": answer, "correct": correct, "false_safe": false_safe,
            "valid_witness": valid_witness, "abstained": decision == "UNRESOLVED",
            "accepted": decision in ("SAFE", "UNSAFE"),
            "error_accepted": decision in ("SAFE", "UNSAFE") and not correct,
            "false_assurance_evidence": evidence,
            "oracle_ceiling": oracle_gate(original, candidate, certificate) if local else None}


def expected_calls(cases):
    return sum(2 if c["group"] == "natural" else 3 for c in cases)


def collect_records(dataset, split, adapter, manifest_hash, emit=None,
                    call_function=call_once, case_order=None, condition_order=None):
    """Shared mathematical execution only; each acquisition mode must audit itself."""
    audit_dataset(dataset)
    cases = dataset["splits"][split]
    if case_order is not None:
        by_id = {case["id"]: case for case in cases}
        if len(case_order) != len(cases) or set(case_order) != set(by_id):
            raise SchemaError("invalid frozen case order")
        cases = [by_id[case_id] for case_id in case_order]
    started = time.perf_counter()
    run = {"version": 1, "split": split, "dataset_hash": digest(dataset),
           "manifest_hash": manifest_hash, "adapter": adapter.configuration,
           "started_at": timestamp(), "scheduled_calls": expected_calls(cases),
           "calls": [], "outcomes": []}
    emit = emit or (lambda event: None)
    emit({"event": "run_start", "metadata": {k: v for k, v in run.items()
                                               if k not in ("calls", "outcomes")}})

    def append_call(record):
        run["calls"].append(record)
        emit({"event": "call", "record": record})

    def append_outcome(outcome):
        run["outcomes"].append(outcome)
        emit({"event": "outcome", "record": outcome})

    rng = random.Random(dataset["seed"] + (19 if split == "dev" else 71))
    for case in cases:
        variables = case["original"]["variables"]
        translation_status = None
        if case["group"] == "natural":
            translation = call_function(adapter, translation_request(case), variables)
            append_call(translation)
            translation_status = translation["status"]
            if translation_status != "completed":
                review = skipped_review(case)
                append_call(review)
                append_outcome(score(case, "B", None, None, review, translation_status))
                continue
            candidate = translation["parsed"]
            certificate = solve(candidate)
            conditions = ["B"]
        else:
            candidate, certificate = case["candidate"], case["certificate"]
            conditions = ["B", "N", "S"]
            rng.shuffle(conditions)
            if condition_order is not None:
                conditions = condition_order[case["id"]]
                if sorted(conditions) != ["B", "N", "S"]:
                    raise SchemaError("invalid frozen condition order")
        if not verify(candidate, certificate)["valid"]:
            raise AssertionError("local certificate failed independent verification")
        # The same serialized candidate/certificate is reused in all three arms.
        for condition in conditions:
            req = review_request(case, candidate, certificate, condition)
            record = call_function(adapter, req, variables)
            append_call(record)
            append_outcome(score(case, condition, candidate, certificate, record, translation_status))
    run["finished_at"] = timestamp()
    run["elapsed_seconds"] = time.perf_counter() - started
    return run


def run_pipeline(dataset, split, adapter, manifest_hash, emit=None):
    if adapter.configuration.get("kind") not in ("synthetic_test_double", "offline_transcript_replay"):
        raise SchemaError("offline runner rejects live adapters")
    run = collect_records(dataset, split, adapter, manifest_hash, emit)
    run["new_model_calls"] = 0
    audit_run(dataset, run)
    emit = emit or (lambda event: None)
    emit({"event": "run_end", "run_hash": digest(run), "finished_at": run["finished_at"]})
    return run


def audit_run(dataset, run):
    """Reconstruct requests and scores from raw records; reject dropped/edited pairs."""
    audit_dataset(dataset)
    keys(run, ("version", "split", "dataset_hash", "manifest_hash", "adapter", "started_at",
               "scheduled_calls", "new_model_calls", "calls", "outcomes", "finished_at", "elapsed_seconds"))
    if (type(run["version"]) is not int or run["version"] != 1
            or type(run["new_model_calls"]) is not int or run["new_model_calls"] != 0
            or run["adapter"].get("kind") not in ("synthetic_test_double", "offline_transcript_replay")):
        raise SchemaError("invalid offline run metadata")
    if run["dataset_hash"] != digest(dataset) or run["split"] not in dataset["splits"]:
        raise SchemaError("run/dataset binding mismatch")
    return audit_content(dataset, run)


def audit_content(dataset, run, live=False):
    """Recompute all mathematics. Live provenance/billing requires a separate audit."""
    cases = dataset["splits"][run["split"]]
    if run["scheduled_calls"] != expected_calls(cases) or len(run["calls"]) != expected_calls(cases):
        raise SchemaError("missing scheduled call records")
    records = {}
    for record in run["calls"]:
        keys(record, ("request", "status", "response_text", "usage", "parsed", "error",
                      "adapter_invoked", "started_at", "latency_seconds"))
        req = record["request"]
        if req["id"] in records:
            raise SchemaError("duplicate call record")
        records[req["id"]] = record
        if record["usage"] is not None:
            validate_usage(record["usage"])
        statuses = ("completed", "schema_error", "missing", "transport_error", "blocked_translation")
        if live:
            statuses += ("truncated", "refused", "integrity_error", "budget_blocked", "not_attempted")
        if record["status"] not in statuses:
            raise SchemaError("unknown call status")
        skipped = ("blocked_translation", "budget_blocked", "not_attempted") if live else ("blocked_translation",)
        if (type(record["adapter_invoked"]) is not bool
                or record["adapter_invoked"] != (record["status"] not in skipped)
                or type(record["latency_seconds"]) not in (int, float)
                or not math.isfinite(record["latency_seconds"]) or record["latency_seconds"] < 0):
            raise SchemaError("invalid invocation/latency record")
        unavailable = (("missing", "blocked_translation", "budget_blocked", "not_attempted") if live
                       else ("missing", "transport_error", "blocked_translation"))
        if record["status"] in unavailable:
            if record["response_text"] is not None or record["usage"] is not None:
                raise SchemaError("unavailable response carries response/usage data")
        if record["status"] == "completed":
            # Parsing is repeated below against the actual case variables.
            if record["response_text"] is None or record["usage"] is None:
                raise SchemaError("completed call lacks response/usage")
        elif record["parsed"] is not None:
            raise SchemaError("failed call must not have parsed output")
    outcomes = {}
    for outcome in run["outcomes"]:
        key = outcome["case_id"], outcome["condition"]
        if key in outcomes:
            raise SchemaError("duplicate outcome")
        outcomes[key] = outcome
    expected_ids, expected_outcomes = set(), set()
    for case in cases:
        variables = case["original"]["variables"]
        translation_status = None
        if case["group"] == "natural":
            req = translation_request(case)
            expected_ids.add(req["id"])
            record = records.get(req["id"])
            if record is None or record["request"] != req:
                raise SchemaError("translation request mismatch")
            translation_status = record["status"]
            candidate = _audit_parse(record, parse_translation, variables)
            certificate = solve(candidate) if candidate is not None else None
            conditions = ["B"]
        else:
            candidate, certificate = case["candidate"], case["certificate"]
            conditions = ["B", "N", "S"]
        for condition in conditions:
            key = case["id"], condition
            req_id = f"{case['id']}:reviewer:{condition}"
            expected_ids.add(req_id)
            expected_outcomes.add(key)
            record = records.get(req_id)
            if record is None:
                raise SchemaError("missing reviewer call")
            if candidate is None:
                if (record["status"] != "blocked_translation" or record["adapter_invoked"]
                        or record["request"] != skipped_review(case)["request"]):
                    raise SchemaError("review must be skipped after invalid translation")
            else:
                req = review_request(case, candidate, certificate, condition)
                if record["request"] != req:
                    raise SchemaError("review request/evidence mismatch")
                _audit_parse(record, parse_review, variables)
            expected = score(case, condition, candidate, certificate, record, translation_status)
            if canonical(outcomes.get(key)) != canonical(expected):
                raise SchemaError("saved outcome disagrees with independent rescoring")
    if set(records) != expected_ids or set(outcomes) != expected_outcomes:
        raise SchemaError("unexpected or missing case/condition")
    return {"valid": True, "calls": len(records), "outcomes": len(outcomes),
            "confirmed_false_guarantees": sum(o["false_safe"] for o in outcomes.values())}


def _audit_parse(record, parser, variables):
    if record["status"] == "completed":
        parsed = parser(record["response_text"], variables)
        if parsed != record["parsed"]:
            raise SchemaError("parsed output does not match raw response")
        return parsed
    if record["status"] == "schema_error" and record["response_text"] is not None:
        try:
            parser(record["response_text"], variables)
            validate_usage(record["usage"])
        except SchemaError:
            return None
        raise SchemaError("schema error record contains a valid response")
    return None


def pilot_gate(dataset, run):
    audit_run(dataset, run)
    return pilot_statistics(run, "synthetic gate rehearsal" if run["adapter"]["kind"] ==
                            "synthetic_test_double" else "offline recorded-response pilot gate")


def pilot_statistics(run, interpretation):
    if run["split"] != "dev":
        raise SchemaError("pilot gate requires development data")
    valid = sum(call["status"] == "completed" for call in run["calls"])
    clean = {}
    for outcome in run["outcomes"]:
        if outcome["group"] in ("natural", "equivalent"):
            clean.setdefault(outcome["case_id"], []).append(outcome["correct"])
    correct = sum(all(values) for values in clean.values())
    return {"valid_responses": valid, "scheduled_responses": run["scheduled_calls"],
            "clean_cases_correct_in_all_conditions": correct, "clean_cases": len(clean),
            "passed": valid / run["scheduled_calls"] >= 0.90 and correct / len(clean) >= 0.80,
            "interpretation": interpretation}
