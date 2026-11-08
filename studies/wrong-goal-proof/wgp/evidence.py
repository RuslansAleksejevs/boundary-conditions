"""Standalone, independently checkable false-guarantee packets.

Mathematical validation is not authentication of a model response's provenance.
Every claim remains labeled with its source adapter mode.
"""

from .adapters import parse_review
from .certificates import verify
from .logic import (SchemaError, canonical, contract_hash, digest, keys,
                    scalar_witness, validate_contract)
from .pipeline import audit_run
from .vector import witness_valid


def export_evidence(dataset, run):
    audit_run(dataset, run)
    originals = {c["id"]: c["original"] for c in dataset["splits"][run["split"]]}
    cases = {}
    for outcome in run["outcomes"]:
        if not outcome["false_safe"]:
            continue
        case_id = outcome["case_id"]
        case = cases.setdefault(case_id, {
            "case_id": case_id, "group": outcome["group"], "family": outcome["family"],
            "original": originals[case_id], "candidate": outcome["candidate"],
            "certificate": outcome["certificate"],
            "evidence": outcome["false_assurance_evidence"], "answers": {}})
        case["answers"][outcome["condition"]] = outcome["answer"]
    packet = {"version": 1, "mode": run["adapter"]["kind"],
              "source_run_hash": digest(run), "dataset_hash": digest(dataset),
              "cases": list(cases.values())}
    verify_evidence(packet)
    return packet


def verify_evidence(packet):
    keys(packet, ("version", "mode", "source_run_hash", "dataset_hash", "cases"))
    if (type(packet["version"]) is not int or packet["version"] != 1
            or packet["mode"] not in ("synthetic_test_double", "offline_transcript_replay")
            or type(packet["cases"]) is not list):
        raise SchemaError("invalid evidence envelope")
    seen, guarantees = set(), 0
    for case in packet["cases"]:
        keys(case, ("case_id", "group", "family", "original", "candidate", "certificate", "evidence", "answers"))
        if type(case["case_id"]) is not str or case["case_id"] in seen:
            raise SchemaError("duplicate evidence case")
        seen.add(case["case_id"])
        original, candidate = case["original"], case["candidate"]
        validate_contract(original)
        validate_contract(candidate)
        if not verify(candidate, case["certificate"])["valid"]:
            raise SchemaError("local certificate invalid")
        evidence = case["evidence"]
        keys(evidence, ("original_hash", "candidate_hash", "certificate_hash", "witness",
                        "scalar_confirmed", "vector_confirmed"))
        if (evidence["original_hash"] != contract_hash(original)
                or evidence["candidate_hash"] != contract_hash(candidate)
                or evidence["certificate_hash"] != digest(case["certificate"], "wgp-certificate-v1")):
            raise SchemaError("evidence hash mismatch")
        if (evidence["scalar_confirmed"] is not True or evidence["vector_confirmed"] is not True
                or not scalar_witness(original, evidence["witness"])
                or not witness_valid(original, evidence["witness"])):
            raise SchemaError("false guarantee lacks independently valid original witness")
        if type(case["answers"]) is not dict or not case["answers"] or not set(case["answers"]) <= {"B", "N", "S"}:
            raise SchemaError("invalid answer conditions")
        for answer in case["answers"].values():
            parsed = parse_review(canonical(answer), original["variables"])
            if parsed["verdict"] != "SAFE":
                raise SchemaError("not a SAFE guarantee")
            guarantees += 1
    return {"valid": True, "mode": packet["mode"], "cases": len(seen),
            "independently_confirmed_false_guarantees": guarantees,
            "provenance_authenticated": False}
