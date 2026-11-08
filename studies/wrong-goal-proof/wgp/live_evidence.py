"""Actual-answer counterexamples; never relabel an offline evidence packet."""

from .adapters import parse_review
from .evidence import mathematical_cases, verify_mathematical_cases
from .live import LIVE_KIND, audit_live
from .live_http import interpret_receipt, payload_for, validate_configuration
from .logic import SchemaError, canonical, digest, keys, render_contract
from .prompts import review_request


def export_live_evidence(dataset, manifest, run):
    audit_live(dataset, manifest, run)
    cases = mathematical_cases(dataset, run)
    receipts = {receipt["logical_id"]: receipt for receipt in run["receipts"]}
    for case in cases:
        case["acquisitions"] = {}
        for condition in case["answers"]:
            request_id = case["case_id"] + ":reviewer:" + condition
            receipt = receipts[request_id]
            case["acquisitions"][condition] = {
                "provider_request_id": interpret_receipt(receipt, manifest["configuration"])["provider_request_id"],
                "receipt_hash": digest(receipt, "wgp-receipt-v1"), "receipt": receipt}
    packet = {"version": 1, "mode": LIVE_KIND, "source_run_hash": digest(run),
              "manifest_hash": digest(manifest), "dataset_hash": digest(dataset),
              "configuration": manifest["configuration"], "cases": cases,
              "provenance_note": "Locally recorded HTTPS receipts, not cryptographically authenticated provider attestations."}
    verify_live_evidence(packet)
    return packet


def verify_live_evidence(packet):
    keys(packet, ("version", "mode", "source_run_hash", "manifest_hash", "dataset_hash",
                  "configuration", "cases", "provenance_note"))
    if type(packet["version"]) is not int or packet["version"] != 1 or packet["mode"] != LIVE_KIND:
        raise SchemaError("not a live counterexample packet")
    config = validate_configuration(packet["configuration"])
    if type(packet["cases"]) is not list:
        raise SchemaError("live evidence cases must be a list")
    mathematical = []
    seen = set()
    for case in packet["cases"]:
        keys(case, ("case_id", "group", "family", "original", "candidate", "certificate",
                    "evidence", "answers", "acquisitions"))
        if type(case["acquisitions"]) is not dict or set(case["acquisitions"]) != set(case["answers"]):
            raise SchemaError("every false guarantee needs its actual acquisition")
        for condition, acquisition in case["acquisitions"].items():
            keys(acquisition, ("provider_request_id", "receipt_hash", "receipt"))
            receipt = acquisition["receipt"]
            interpreted = interpret_receipt(receipt, config)
            request = review_request({"id": case["case_id"], "task": render_contract(case["original"])},
                                     case["candidate"], case["certificate"], condition)
            pid = acquisition["provider_request_id"]
            if (receipt["transport_kind"] != "official_openrouter_http"
                    or receipt["logical_id"] != case["case_id"] + ":reviewer:" + condition
                    or acquisition["receipt_hash"] != digest(receipt, "wgp-receipt-v1")
                    or receipt["payload"] != payload_for(request, config)
                    or receipt["payload_hash"] != digest(receipt["payload"], "wgp-http-request-v1")
                    or receipt["prompt_hash"] != request["prompt_hash"]
                    or interpreted["status"] != "response" or pid != interpreted["provider_request_id"]
                    or pid in seen):
                raise SchemaError("false guarantee acquisition binding mismatch")
            seen.add(pid)
            answer = parse_review(interpreted["text"], case["original"]["variables"])
            if canonical(answer) != canonical(case["answers"][condition]):
                raise SchemaError("guarantee differs from visible provider answer")
        mathematical.append({k: v for k, v in case.items() if k != "acquisitions"})
    return {**verify_mathematical_cases(mathematical), "mode": LIVE_KIND,
            "acquisition_ids": len(seen), "provenance_authenticated": False}