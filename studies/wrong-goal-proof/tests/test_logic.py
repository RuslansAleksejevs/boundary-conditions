import copy
import random
import unittest

from wgp.dataset import random_expr
from wgp.logic import (SchemaError, assignments, canonical, const, contract,
                       contract_hash, neg, op, parse_rendered_contract,
                       parse_rendered_expr, render_contract, scalar, strict_json,
                       validate_contract, validate_expr, validate_state, var)
from wgp.vector import fidelity, state_at, state_index, tables, truth, vector


class StrictLanguageTests(unittest.TestCase):
    def setUp(self):
        self.c = contract(var("p"), var("q"))

    def test_contract_roundtrip(self):
        self.assertEqual(validate_contract(strict_json(canonical(self.c))), self.c)

    def test_duplicate_json_keys(self):
        with self.assertRaises(SchemaError):
            strict_json('{"C":true,"C":false}')

    def test_nonfinite_json(self):
        for text in ("NaN", "Infinity", "-Infinity", "1e999"):
            with self.subTest(text=text), self.assertRaises(SchemaError):
                strict_json(text)

    def test_not_json_or_fenced_json(self):
        for text in ('```json\n{}\n```', '{', 'true false', None):
            with self.subTest(text=text), self.assertRaises(SchemaError):
                strict_json(text)

    def test_response_size_bound(self):
        with self.assertRaises(SchemaError):
            strict_json('"' + 'a' * 200_000 + '"')

    def test_invalid_unicode_is_schema_error(self):
        with self.assertRaises(SchemaError):
            strict_json('"' + chr(0xD800) + '"')

    def test_deep_json(self):
        with self.assertRaises(SchemaError):
            strict_json("[" * 2000 + "0" + "]" * 2000)

    def test_unknown_and_extra_contract_keys(self):
        for value in ({**self.c, "task_id": "not-binding"}, {"C": var("p")}, [], None):
            with self.subTest(value=value), self.assertRaises(SchemaError):
                validate_contract(value)

    def test_variable_schema(self):
        for variables in ([], ["q", "p"], ["p", "p"], ["x"], "pq", [1], ["p", "q", "r", "s", "t", "u"]):
            with self.subTest(variables=variables), self.assertRaises(SchemaError):
                validate_contract({**self.c, "variables": variables})

    def test_unknown_variable(self):
        with self.assertRaises(SchemaError):
            validate_contract({**self.c, "Q": var("x")})

    def test_strict_node_keys_and_types(self):
        malformed = [True, 1, [], {}, {"const": 1}, {"const": "true"},
                     {"var": "p", "const": True}, {"var": ["p"]},
                     {"op": "xor", "args": [var("p"), var("q")]},
                     {"op": "and", "args": []}, {"op": "or", "args": [var("p")]},
                     {"op": "not", "args": [var("p")]},
                     {"op": "not", "arg": var("p"), "extra": False}]
        for expr in malformed:
            with self.subTest(expr=expr), self.assertRaises(SchemaError):
                validate_expr(expr, self.c["variables"])

    def test_depth_bound_and_cycle(self):
        expr = var("p")
        for _ in range(12):
            expr = neg(expr)
        cycle = {"op": "not"}
        cycle["arg"] = cycle
        for item in (expr, cycle):
            with self.assertRaises(SchemaError):
                validate_expr(item, self.c["variables"])

    def test_node_count_bound(self):
        expr = var("p")
        for _ in range(7):
            expr = op("and", expr, expr)
        with self.assertRaises(SchemaError):
            validate_expr(expr, self.c["variables"])

    def test_state_strictness(self):
        for state in ({"p": True}, {"p": 1, "q": False}, {"p": True, "q": False, "x": True}):
            with self.subTest(state=state), self.assertRaises(SchemaError):
                validate_state(state, ["p", "q"])

    def test_canonical_hash_key_order(self):
        other = {key: self.c[key] for key in reversed(self.c)}
        self.assertEqual(contract_hash(self.c), contract_hash(other))

    def test_hash_binds_both_functions(self):
        changed_c = {**self.c, "C": op("and", var("p"), var("q"))}
        changed_q = {**self.c, "Q": neg(var("q"))}
        self.assertNotEqual(contract_hash(self.c), contract_hash(changed_c))
        self.assertNotEqual(contract_hash(self.c), contract_hash(changed_q))

    def test_open_functions_distinct_from_closed_truth(self):
        a = contract(var("p"), var("p"))
        b = contract(var("q"), var("q"))
        result = fidelity(a, b)
        self.assertTrue(result["closed_truth_equal"])
        self.assertFalse(result["C_equal"])
        self.assertFalse(result["Q_equal"])

    def test_changed_contract_can_still_answer_original_correctly(self):
        a = contract(var("p"), var("p"))
        b = contract(op("and", var("p"), var("q")), var("p"))
        self.assertFalse(fidelity(a, b)["open_functions_equal"])
        self.assertEqual(truth(a)["verdict"], truth(b)["verdict"])

    def test_equivalence_is_not_syntactic_identity(self):
        a = contract(op("and", var("p"), var("q")), var("p"))
        b = contract(op("and", var("q"), var("p")), var("p"))
        self.assertNotEqual(contract_hash(a), contract_hash(b))
        self.assertTrue(fidelity(a, b)["open_functions_equal"])


class SemanticProperties(unittest.TestCase):
    def test_assignment_index_roundtrip_3_to_5(self):
        for n in (3, 4, 5):
            variables = list("pqrst"[:n])
            for index, state in enumerate(assignments(variables)):
                self.assertEqual(state_at(index, variables), state)
                self.assertEqual(state_index(state, variables), index)

    def test_known_truth_tables(self):
        variables = ["p", "q"]
        self.assertEqual(vector(var("p"), variables), 0b1100)
        self.assertEqual(vector(var("q"), variables), 0b1010)
        self.assertEqual(vector(op("implies", var("p"), var("q")), variables), 0b1011)
        self.assertEqual(vector(neg(var("p")), variables), 0b0011)

    def test_constants_tautology_contradiction_and_nested_negation(self):
        p = var("p")
        exprs = [const(True), const(False), op("or", p, neg(p)),
                 op("and", p, neg(p)), neg(neg(neg(p))), op("implies", p, p)]
        for n in (3, 4, 5):
            variables = list("pqrst"[:n])
            for expr in exprs:
                bits = vector(expr, variables)
                for i, state in enumerate(assignments(variables)):
                    self.assertEqual(scalar(expr, state), bool(bits & (1 << i)))

    def test_2400_random_formulas_and_renderer(self):
        rng = random.Random(6017)
        for n in (3, 4, 5):
            variables = list("pqrst"[:n])
            for _ in range(800):
                expr = random_expr(rng, variables, depth=4)
                validate_expr(expr, variables)
                bits = vector(expr, variables)
                value = contract(expr, neg(expr), n)
                self.assertEqual(parse_rendered_contract(render_contract(value)), value)
                for index, state in enumerate(assignments(variables)):
                    self.assertEqual(scalar(expr, state), bool(bits & (1 << index)))

    def test_all_256_three_atom_boolean_functions(self):
        # Canonical DNF enumerates every possible open function over three atoms.
        variables = list("pqr")
        states = list(assignments(variables))

        def join(operator, terms):
            if len(terms) == 1:
                return terms[0]
            mid = len(terms) // 2
            return op(operator, join(operator, terms[:mid]), join(operator, terms[mid:]))

        for mask in range(256):
            terms = [join("and", [var(v) if state[v] else neg(var(v)) for v in variables])
                     for i, state in enumerate(states) if mask & (1 << i)]
            expr = join("or", terms) if terms else const(False)
            validate_expr(expr, variables)
            self.assertEqual(vector(expr, variables), mask)
            self.assertEqual(sum(int(scalar(expr, state)) << i for i, state in enumerate(states)), mask)

    def test_renderer_rejects_ambiguous_extra_or_changed_text(self):
        for text in ("p AND q", "(p OR)", "(p XOR q)", "(NOT p", "(p OR q) x", "p;pass"):
            with self.subTest(text=text), self.assertRaises(SchemaError):
                parse_rendered_expr(text, ["p", "q"])
        text = render_contract(contract(var("p"), var("q")))
        with self.assertRaises(SchemaError):
            parse_rendered_contract(text.replace("EVERY", "SOME"))


if __name__ == "__main__":
    unittest.main()
