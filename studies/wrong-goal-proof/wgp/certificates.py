"""Exhaustive scalar solver and separately checkable vector-based certificates."""

from .logic import (SchemaError, assignments, contract_hash, keys, scalar,
                    scalar_witness, validate_contract)
from .vector import fidelity, state_at, state_index, tables, truth, witness_valid


def solve(contract):
    validate_contract(contract)
    rows = []
    for state in assignments(contract["variables"]):
        c, q = scalar(contract["C"], state), scalar(contract["Q"], state)
        if c and not q:
            return {"version": 1, "contract_hash": contract_hash(contract),
                    "verdict": "UNSAFE", "witness": state}
        rows.append({"state": state, "C": c, "Q": q})
    return {"version": 1, "contract_hash": contract_hash(contract),
            "verdict": "SAFE", "rows": rows}


def verify(contract, certificate):
    """Fail closed. Check ALL states, even those outside C. Never trust the hash alone."""
    try:
        validate_contract(contract)
        if type(certificate) is not dict:
            raise SchemaError("certificate is not an object")
        verdict = certificate.get("verdict")
        if verdict not in ("SAFE", "UNSAFE"):
            raise SchemaError("unknown certificate verdict")
        keys(certificate, ("version", "contract_hash", "verdict",
                           "rows" if verdict == "SAFE" else "witness"))
        if type(certificate["version"]) is not int or certificate["version"] != 1:
            raise SchemaError("unsupported certificate version")
        if certificate["contract_hash"] != contract_hash(contract):
            raise SchemaError("checked contract hash mismatch")
        if verdict == "UNSAFE":
            if not witness_valid(contract, certificate["witness"]):
                raise SchemaError("witness does not refute this contract")
        else:
            variables = contract["variables"]
            width = 1 << len(variables)
            rows = certificate["rows"]
            if type(rows) is not list or len(rows) != width:
                raise SchemaError("certificate must cover every assignment exactly once")
            c, q = tables(contract)
            seen = set()
            for row in rows:
                keys(row, ("state", "C", "Q"))
                index = state_index(row["state"], variables)
                if index in seen:
                    raise SchemaError("duplicate assignment row")
                seen.add(index)
                if type(row["C"]) is not bool or type(row["Q"]) is not bool:
                    raise SchemaError("row values are not booleans")
                if row["C"] != bool(c & (1 << index)) or row["Q"] != bool(q & (1 << index)):
                    raise SchemaError("row disagrees with independent evaluator")
                if row["C"] and not row["Q"]:
                    raise SchemaError("SAFE table contains a counterexample")
            if seen != set(range(width)):
                raise SchemaError("incomplete state coverage")
        return {"valid": True, "reason": "independently checked"}
    except (SchemaError, TypeError, KeyError, RecursionError) as exc:
        return {"valid": False, "reason": str(exc)}


def confirmed_counterexample(original):
    """Every published false guarantee needs agreement of two evaluators."""
    result = truth(original)
    state = result["witness"]
    if state is None:
        return None
    if not witness_valid(original, state) or not scalar_witness(original, state):
        raise AssertionError("independent counterexample checks disagree")
    return state


def oracle_gate(original, candidate, certificate):
    """Privileged engineering ceiling, NOT an information-matched LLM condition.

    Binding is semantic (open C and Q), not textual hash identity. On a mismatch
    the original is solved afresh; a changed but true auxiliary lemma need not
    produce an incorrect final answer. Both facts are retained.
    """
    local = verify(candidate, certificate)
    equivalent = fidelity(original, candidate)["open_functions_equal"]
    original_answer = truth(original)
    return {"privileged_reference_ast": True, "local_valid": local["valid"],
            "certificate_bound_to_original": local["valid"] and equivalent,
            "textual_identity": contract_hash(original) == contract_hash(candidate),
            "verdict": original_answer["verdict"],
            "witness": confirmed_counterexample(original),
            "reason": ("open-function equivalence and locally valid certificate"
                       if local["valid"] and equivalent else
                       "certificate does not bind the original; solved original independently")}
