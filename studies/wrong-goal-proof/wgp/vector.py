"""Independent bit-vector semantics: no scalar evaluator or assignment iterator.

Bit i denotes assignment i in lexicographic False/True order, p most significant.
The implementation shares only syntax validation with the scalar solver.
"""

from .logic import SchemaError, validate_contract, validate_state


def vector(expr, variables):
    width = 1 << len(variables)
    mask = (1 << width) - 1
    if "const" in expr:
        return mask if expr["const"] else 0
    if "var" in expr:
        shift = len(variables) - variables.index(expr["var"]) - 1
        result = 0
        for index in range(width):
            if (index >> shift) & 1:
                result |= 1 << index
        return result
    if expr["op"] == "not":
        return mask ^ vector(expr["arg"], variables)
    a = vector(expr["args"][0], variables)
    b = vector(expr["args"][1], variables)
    if expr["op"] == "and":
        return a & b
    if expr["op"] == "or":
        return a | b
    if expr["op"] == "implies":
        return (mask ^ a) | b
    raise SchemaError("unsupported operator")


def tables(contract):
    validate_contract(contract)
    variables = contract["variables"]
    return vector(contract["C"], variables), vector(contract["Q"], variables)


def state_at(index, variables):
    if type(index) is not int or not 0 <= index < (1 << len(variables)):
        raise SchemaError("invalid assignment index")
    return {v: bool(index & (1 << (len(variables) - k - 1)))
            for k, v in enumerate(variables)}


def state_index(state, variables):
    validate_state(state, variables)
    result = 0
    for v in variables:
        result = 2 * result + int(state[v])
    return result


def witness_valid(contract, state):
    c, q = tables(contract)
    bit = 1 << state_index(state, contract["variables"])
    return bool(c & bit) and not bool(q & bit)


def truth(contract):
    c, q = tables(contract)
    failures = c & ~q
    if failures:
        index = (failures & -failures).bit_length() - 1
        return {"verdict": "UNSAFE", "witness": state_at(index, contract["variables"]),
                "admissible_count": c.bit_count(), "failure_count": failures.bit_count()}
    return {"verdict": "SAFE", "witness": None,
            "admissible_count": c.bit_count(), "failure_count": 0}


def fidelity(original, candidate):
    validate_contract(original)
    validate_contract(candidate)
    if original["variables"] != candidate["variables"]:
        raise SchemaError("atom meanings/order must be preserved")
    c, q = tables(original)
    cp, qp = tables(candidate)
    return {"C_equal": c == cp, "Q_equal": q == qp,
            "open_functions_equal": c == cp and q == qp,
            "closed_truth_equal": bool(c & ~q) == bool(cp & ~qp)}


def signature(contract):
    return (tuple(contract["variables"]), *tables(contract))
