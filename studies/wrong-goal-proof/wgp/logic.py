"""Strict JSON language, canonical encoding, scalar semantics, and rendering.

Atoms have fixed meanings and order. Equality of the open C and Q functions is
a study convention, not a general criterion for faithful mathematics.
"""

import hashlib
import itertools
import json
import math
import re


class SchemaError(ValueError):
    """An input is outside the deliberately small supported language."""


MAX_DEPTH = 10
MAX_NODES = 127
MAX_JSON_BYTES = 200_000
ATOMS = ("p", "q", "r", "s", "t")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def digest(value, domain="wgp-v1"):
    return hashlib.sha256((domain + "\n" + canonical(value)).encode()).hexdigest()


def strict_json(text, max_bytes=MAX_JSON_BYTES):
    if not isinstance(text, str):
        raise SchemaError("JSON must be a bounded UTF-8 string")
    try:
        byte_count = len(text.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise SchemaError("JSON text contains invalid Unicode") from exc
    if byte_count > max_bytes:
        raise SchemaError("JSON must be a bounded UTF-8 string")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise SchemaError("duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise SchemaError("non-finite JSON number: " + value)

    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise SchemaError("overflowing JSON number")
        return result

    try:
        result = json.loads(text, object_pairs_hook=pairs,
                            parse_constant=invalid_constant, parse_float=finite_float)
        # Python versions differ in JSON recursion limits. Bound nesting explicitly
        # before callers traverse arbitrary decoded values.
        stack = [(result, 0)]
        while stack:
            value, depth = stack.pop()
            if depth > 64:
                raise SchemaError("JSON nesting exceeds 64 levels")
            if type(value) is dict:
                stack.extend((child, depth + 1) for child in value.values())
            elif type(value) is list:
                stack.extend((child, depth + 1) for child in value)
        return result
    except (ValueError, TypeError, RecursionError) as exc:
        raise SchemaError(str(exc)) from exc


def keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise SchemaError("expected exactly these keys: " + ", ".join(expected))


def variables_valid(variables):
    if (type(variables) is not list or not 1 <= len(variables) <= 5
            or any(type(v) is not str or v not in ATOMS for v in variables)
            or len(set(variables)) != len(variables)
            or variables != list(ATOMS[:len(variables)])):
        raise SchemaError("variables must be an ordered prefix of p,q,r,s,t")


def validate_expr(expr, variables):
    count = 0

    def visit(node, depth):
        nonlocal count
        count += 1
        if depth > MAX_DEPTH or count > MAX_NODES or type(node) is not dict:
            raise SchemaError("AST exceeds limits or contains a non-object node")
        if "var" in node:
            keys(node, ("var",))
            if type(node["var"]) is not str or node["var"] not in variables:
                raise SchemaError("unknown variable")
        elif "const" in node:
            keys(node, ("const",))
            if type(node["const"]) is not bool:
                raise SchemaError("constants must be JSON booleans, not numbers")
        elif node.get("op") == "not":
            keys(node, ("op", "arg"))
            visit(node["arg"], depth + 1)
        elif node.get("op") in ("and", "or", "implies"):
            keys(node, ("op", "args"))
            if type(node["args"]) is not list or len(node["args"]) != 2:
                raise SchemaError("binary operators require exactly two arguments")
            for child in node["args"]:
                visit(child, depth + 1)
        else:
            raise SchemaError("unsupported AST operator")

    visit(expr, 0)


def validate_contract(contract):
    keys(contract, ("variables", "C", "Q"))
    variables_valid(contract["variables"])
    for name in ("C", "Q"):
        validate_expr(contract[name], contract["variables"])
    return contract


def contract_hash(contract):
    validate_contract(contract)
    return digest(contract, "wgp-contract-v1")


def var(name):
    return {"var": name}


def const(value):
    return {"const": value}


def neg(arg):
    return {"op": "not", "arg": arg}


def op(name, left, right):
    return {"op": name, "args": [left, right]}


def contract(c, q, n=4):
    result = {"variables": list(ATOMS[:n]), "C": c, "Q": q}
    return validate_contract(result)


def assignments(variables):
    for values in itertools.product((False, True), repeat=len(variables)):
        yield dict(zip(variables, values))


def validate_state(state, variables):
    keys(state, variables)
    if any(type(value) is not bool for value in state.values()):
        raise SchemaError("state values must be booleans")
    return state


def scalar(expr, state):
    """Recursive scalar evaluator; callers validate AST and assignment first."""
    if "var" in expr:
        return state[expr["var"]]
    if "const" in expr:
        return expr["const"]
    if expr["op"] == "not":
        return not scalar(expr["arg"], state)
    left, right = (scalar(arg, state) for arg in expr["args"])
    if expr["op"] == "and":
        return left and right
    if expr["op"] == "or":
        return left or right
    if expr["op"] == "implies":
        return (not left) or right
    raise SchemaError("unsupported operator")


def scalar_witness(contract, state):
    validate_contract(contract)
    validate_state(state, contract["variables"])
    return scalar(contract["C"], state) and not scalar(contract["Q"], state)


def render_expr(expr):
    if "var" in expr:
        return expr["var"]
    if "const" in expr:
        return "TRUE" if expr["const"] else "FALSE"
    if expr["op"] == "not":
        return "(NOT " + render_expr(expr["arg"]) + ")"
    left, right = (render_expr(arg) for arg in expr["args"])
    return "(" + left + " " + expr["op"].upper() + " " + right + ")"


def render_contract(value):
    validate_contract(value)
    return ("Variables: " + ", ".join(value["variables"]) + "\n"
            "Each variable denotes its own fixed Boolean input; meanings cannot be renamed.\n"
            "Admissible C: " + render_expr(value["C"]) + "\n"
            "Required Q: " + render_expr(value["Q"]) + "\n"
            "Question: does Q hold for EVERY assignment satisfying C?\n"
            "Return UNSAFE with a concrete C=true, Q=false assignment if not.\n"
            "An empty admissible domain makes the universal claim vacuously SAFE.")


def parse_rendered_expr(text, variables):
    """Small grammar used to test rendering and by explicitly synthetic adapters."""
    tokens = re.findall(r"[A-Za-z]+|[()]", text)
    if re.sub(r"\s+", "", text) != "".join(tokens) or len(tokens) > 512:
        raise SchemaError("unsupported rendered tokens")
    cursor = 0

    def read(depth=0):
        nonlocal cursor
        if depth > MAX_DEPTH or cursor >= len(tokens):
            raise SchemaError("incomplete or too deep rendered expression")
        token = tokens[cursor]
        cursor += 1
        if token in variables:
            return var(token)
        if token in ("TRUE", "FALSE"):
            return const(token == "TRUE")
        if token != "(":
            raise SchemaError("expected parenthesized expression")
        if cursor < len(tokens) and tokens[cursor] == "NOT":
            cursor += 1
            result = neg(read(depth + 1))
        else:
            left = read(depth + 1)
            if cursor >= len(tokens) or tokens[cursor] not in ("AND", "OR", "IMPLIES"):
                raise SchemaError("expected binary operator")
            operator = tokens[cursor].lower()
            cursor += 1
            result = op(operator, left, read(depth + 1))
        if cursor >= len(tokens) or tokens[cursor] != ")":
            raise SchemaError("expected closing parenthesis")
        cursor += 1
        return result

    result = read()
    if cursor != len(tokens):
        raise SchemaError("trailing tokens")
    validate_expr(result, variables)
    return result


def parse_rendered_contract(text):
    lines = text.splitlines()
    if len(lines) != 7 or not lines[0].startswith("Variables: "):
        raise SchemaError("invalid controlled contract")
    variables = lines[0].removeprefix("Variables: ").split(", ")
    variables_valid(variables)
    if not lines[2].startswith("Admissible C: ") or not lines[3].startswith("Required Q: "):
        raise SchemaError("missing controlled C/Q fields")
    value = {"variables": variables,
             "C": parse_rendered_expr(lines[2].removeprefix("Admissible C: "), variables),
             "Q": parse_rendered_expr(lines[3].removeprefix("Required Q: "), variables)}
    if render_contract(value) != text:
        raise SchemaError("controlled contract wording changed")
    return value
