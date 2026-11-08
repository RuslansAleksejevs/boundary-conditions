"""Seeded synthetic contracts selected only by mathematical properties.

Selection never uses reviewer outcomes. Holdout excludes both open-function
duplicates and original AST skeletons seen in development (not just renamings).
This is still a narrow, template-dependent stress test, not a random-world sample.
"""

import random

from .certificates import solve, verify
from .logic import (SchemaError, const, contract, digest, neg, op, render_contract,
                    validate_contract, var)
from .vector import fidelity, signature, truth


FAULTS = ("restrict_C", "drop_conjunct", "and_to_or", "reverse_implication")
EQUIVALENTS = ("reorder", "de_morgan", "expand_implication", "redundancy")
SIZES = {"dev": {"natural": 8, "fault": 8, "equivalent": 4},
         "holdout": {"natural": 40, "fault": 40, "equivalent": 20}}


def random_expr(rng, variables=("p", "q", "r", "s"), depth=2):
    if depth == 0 or rng.random() < 0.22:
        if rng.random() < 0.08:
            return const(rng.choice((False, True)))
        return var(rng.choice(variables))
    if rng.random() < 0.22:
        return neg(random_expr(rng, variables, depth - 1))
    return op(rng.choice(("and", "or", "implies")),
              random_expr(rng, variables, depth - 1),
              random_expr(rng, variables, depth - 1))


def skeleton(value):
    """An intentionally conservative renaming-invariant syntactic fingerprint."""
    def erase(node):
        if "var" in node:
            return {"var": "ATOM"}
        if "const" in node:
            return node
        if node["op"] == "not":
            return neg(erase(node["arg"]))
        return op(node["op"], *(erase(x) for x in node["args"]))
    return digest({"C": erase(value["C"]), "Q": erase(value["Q"])}, "wgp-skeleton-v1")


def proposal(rng, group, family):
    f, g, h = [random_expr(rng, depth=rng.choice((1, 2, 3))) for _ in range(3)]
    if group == "natural":
        if family == "SAFE":
            original = contract(op("and", f, g), op("or", f, h))
        else:
            original = contract(f, g)
        return original, None
    if family == "restrict_C":
        return contract(f, g), contract(op("and", f, g), g)
    if family == "drop_conjunct":
        return contract(f, op("and", f, g)), contract(f, f)
    if family == "and_to_or":
        return (contract(op("or", f, g), op("and", f, g)),
                contract(op("or", f, g), op("or", f, g)))
    if family == "reverse_implication":
        return contract(f, op("implies", f, g)), contract(f, op("implies", g, f))
    if family == "reorder":
        return contract(op("and", f, g), f), contract(op("and", g, f), f)
    if family == "de_morgan":
        return (contract(op("and", f, g), f),
                contract(neg(op("or", neg(f), neg(g))), f))
    if family == "expand_implication":
        return (contract(op("and", f, g), op("implies", h, f)),
                contract(op("and", f, g), op("or", neg(h), f)))
    if family == "redundancy":
        return contract(f, op("or", f, g)), contract(op("and", f, f), op("or", f, g))
    raise ValueError("unknown family")


def case_valid(original, candidate, group, family):
    result = truth(original)
    if not result["admissible_count"]:
        return False
    if group == "natural":
        return candidate is None and result["verdict"] == family
    if candidate is None or original == candidate:
        return False
    comparison = fidelity(original, candidate)
    local = truth(candidate)
    if local["verdict"] != "SAFE" or not local["admissible_count"]:
        return False
    if group == "fault":
        return result["verdict"] == "UNSAFE" and not comparison["open_functions_equal"]
    return result["verdict"] == "SAFE" and comparison["open_functions_equal"]


def make_dataset(seed=6006):
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("seed must be a uint32")
    rng = random.Random(seed)
    dataset = {"version": 1, "seed": seed, "splits": {}}
    previous_signatures = set()
    previous_shapes = set()
    for split, sizes in SIZES.items():
        cases = []
        split_originals = set()
        split_all_signatures = set()
        split_shapes = set()
        for group, size in sizes.items():
            families = (("SAFE", "UNSAFE") if group == "natural" else
                        FAULTS if group == "fault" else EQUIVALENTS)
            for index in range(size):
                family = families[index % len(families)]
                for _ in range(50_000):
                    original, candidate = proposal(rng, group, family)
                    if not case_valid(original, candidate, group, family):
                        continue
                    sig = signature(original)
                    all_sigs = {sig} | ({signature(candidate)} if candidate else set())
                    shape = skeleton(original)
                    if (sig in split_originals or all_sigs & previous_signatures
                            or shape in previous_shapes):
                        continue
                    break
                else:
                    raise RuntimeError("generator exhausted bounded proposals")
                split_originals.add(sig)
                split_all_signatures.update(all_sigs)
                split_shapes.add(shape)
                cases.append({"id": f"{split}-{group}-{index:03d}", "split": split,
                              "group": group, "family": family, "original": original,
                              "candidate": candidate, "task": render_contract(original),
                              "certificate": solve(candidate) if candidate else None})
        rng.shuffle(cases)
        dataset["splits"][split] = cases
        previous_signatures.update(split_all_signatures)
        previous_shapes.update(split_shapes)
    audit_dataset(dataset)
    return dataset


def audit_dataset(dataset):
    """Revalidate saved input, including math, identity, splits, and row coverage."""
    from .logic import keys
    keys(dataset, ("version", "seed", "splits"))
    if (type(dataset["version"]) is not int or dataset["version"] != 1
            or type(dataset["seed"]) is not int or not 0 <= dataset["seed"] < 2**32):
        raise SchemaError("invalid dataset version/seed")
    keys(dataset["splits"], SIZES)
    ids, earlier_signatures, earlier_shapes = set(), set(), set()
    for split, sizes in SIZES.items():
        cases = dataset["splits"][split]
        if type(cases) is not list or len(cases) != sum(sizes.values()):
            raise SchemaError("incorrect split size")
        originals, all_sigs, shapes = set(), set(), set()
        counts = {}
        for case in cases:
            keys(case, ("id", "split", "group", "family", "original", "candidate",
                        "task", "certificate"))
            if (type(case["id"]) is not str or case["id"] in ids
                    or case["split"] != split or case["group"] not in sizes):
                raise SchemaError("duplicate ID, split mismatch, or unknown group")
            ids.add(case["id"])
            group, family = case["group"], case["family"]
            families = (("SAFE", "UNSAFE") if group == "natural" else
                        FAULTS if group == "fault" else EQUIVALENTS)
            if family not in families:
                raise SchemaError("unknown family")
            counts[group, family] = counts.get((group, family), 0) + 1
            original, candidate = case["original"], case["candidate"]
            validate_contract(original)
            if candidate is not None:
                validate_contract(candidate)
            if not case_valid(original, candidate, group, family):
                raise SchemaError("case fails its mathematical selection criteria")
            if case["task"] != render_contract(original):
                raise SchemaError("task rendering mismatch")
            if candidate is None:
                if case["certificate"] is not None:
                    raise SchemaError("natural pipeline must not freeze a translated candidate")
            elif not verify(candidate, case["certificate"])["valid"]:
                raise SchemaError("invalid frozen certificate")
            sig = signature(original)
            sigs = {sig} | ({signature(candidate)} if candidate else set())
            shape = skeleton(original)
            if sig in originals or sigs & earlier_signatures or shape in earlier_shapes:
                raise SchemaError("duplicate semantics or development/holdout skeleton leakage")
            originals.add(sig)
            all_sigs.update(sigs)
            shapes.add(shape)
        for group, size in sizes.items():
            families = (("SAFE", "UNSAFE") if group == "natural" else
                        FAULTS if group == "fault" else EQUIVALENTS)
            for family in families:
                if counts.get((group, family), 0) != size // len(families):
                    raise SchemaError("unbalanced family counts")
        earlier_signatures.update(all_sigs)
        earlier_shapes.update(shapes)
    return {"valid": True, "dev_cases": 20, "holdout_cases": 100,
            "semantic_overlap": 0, "original_skeleton_overlap": 0}
