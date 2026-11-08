import copy
import random
import unittest

from wgp.certificates import confirmed_counterexample, oracle_gate, solve, verify
from wgp.dataset import random_expr
from wgp.logic import assignments, const, contract, contract_hash, neg, op, scalar_witness, var
from wgp.vector import truth, witness_valid


class CertificateTests(unittest.TestCase):
    def setUp(self):
        self.safe = contract(op("and", var("p"), var("q")), var("q"))
        self.unsafe = contract(var("p"), var("q"))
        self.proof = solve(self.safe)
        self.refutation = solve(self.unsafe)

    def test_safe_complete_table(self):
        self.assertEqual(len(self.proof["rows"]), 16)
        self.assertTrue(verify(self.safe, self.proof)["valid"])

    def test_unsafe_witness(self):
        self.assertEqual(self.refutation["verdict"], "UNSAFE")
        self.assertTrue(verify(self.unsafe, self.refutation)["valid"])

    def test_shuffled_complete_rows_allowed(self):
        self.proof["rows"].reverse()
        self.assertTrue(verify(self.safe, self.proof)["valid"])

    def test_missing_row(self):
        self.proof["rows"].pop()
        self.assertFalse(verify(self.safe, self.proof)["valid"])

    def test_duplicate_row(self):
        self.proof["rows"][-1] = copy.deepcopy(self.proof["rows"][0])
        self.assertFalse(verify(self.safe, self.proof)["valid"])

    def test_extra_row(self):
        self.proof["rows"].append(copy.deepcopy(self.proof["rows"][0]))
        self.assertFalse(verify(self.safe, self.proof)["valid"])

    def test_every_row_value_individually_checked(self):
        for i in range(16):
            for field in ("C", "Q"):
                proof = copy.deepcopy(self.proof)
                proof["rows"][i][field] = not proof["rows"][i][field]
                self.assertFalse(verify(self.safe, proof)["valid"])

    def test_rows_outside_admissible_domain_also_checked(self):
        row = next(row for row in self.proof["rows"] if not row["C"])
        row["Q"] = not row["Q"]
        self.assertFalse(verify(self.safe, self.proof)["valid"])

    def test_wrong_hash(self):
        self.proof["contract_hash"] = "0" * 64
        self.assertFalse(verify(self.safe, self.proof)["valid"])

    def test_copied_original_id_not_binding(self):
        self.proof["original_task_id"] = "original"
        self.assertFalse(verify(self.unsafe, self.proof)["valid"])
        self.assertFalse(verify(self.safe, self.proof)["valid"])

    def test_rebound_hash_does_not_repair_wrong_table(self):
        self.proof["contract_hash"] = contract_hash(self.unsafe)
        self.assertFalse(verify(self.unsafe, self.proof)["valid"])

    def test_fake_safe_table_for_unsafe_contract(self):
        proof = {"version": 1, "verdict": "SAFE", "contract_hash": contract_hash(self.unsafe),
                 "rows": [{"state": s, "C": s["p"], "Q": s["q"]}
                          for s in assignments(self.unsafe["variables"])]}
        self.assertFalse(verify(self.unsafe, proof)["valid"])

    def test_unknown_missing_and_nonboolean_assignment(self):
        mutations = [{"p": True}, {"p": True, "q": False, "r": False, "s": 0},
                     {"p": True, "q": False, "r": False, "s": False, "x": False}]
        for state in mutations:
            proof = copy.deepcopy(self.proof)
            proof["rows"][0]["state"] = state
            self.assertFalse(verify(self.safe, proof)["valid"])

    def test_invalid_boolean_row_values(self):
        for value in (1, 0, "true", None):
            proof = copy.deepcopy(self.proof)
            proof["rows"][0]["Q"] = value
            self.assertFalse(verify(self.safe, proof)["valid"])

    def test_certificate_strict_schema(self):
        for change in ({"version": True}, {"version": 2}, {"extra": 1}, {"verdict": "PASS"}, {"rows": {}}):
            proof = {**self.proof, **change}
            self.assertFalse(verify(self.safe, proof)["valid"])
        self.assertFalse(verify(self.safe, None)["valid"])

    def test_false_witness(self):
        self.refutation["witness"]["p"] = False
        self.assertFalse(verify(self.unsafe, self.refutation)["valid"])

    def test_unknown_variable_in_witness(self):
        self.refutation["witness"]["x"] = True
        self.assertFalse(verify(self.unsafe, self.refutation)["valid"])

    def test_empty_domain_is_vacuously_true_not_main_fault(self):
        empty = contract(const(False), const(False))
        proof = solve(empty)
        self.assertEqual(proof["verdict"], "SAFE")
        self.assertEqual(truth(empty)["admissible_count"], 0)
        self.assertTrue(verify(empty, proof)["valid"])
        gate = oracle_gate(self.unsafe, empty, proof)
        self.assertFalse(gate["certificate_bound_to_original"])
        self.assertEqual(gate["verdict"], "UNSAFE")

    def test_oracle_gate_rejects_false_guarantee_with_exact_witness(self):
        result = oracle_gate(self.unsafe, self.safe, self.proof)
        self.assertTrue(result["local_valid"])
        self.assertFalse(result["certificate_bound_to_original"])
        self.assertEqual(result["verdict"], "UNSAFE")
        self.assertTrue(witness_valid(self.unsafe, result["witness"]))
        self.assertTrue(scalar_witness(self.unsafe, result["witness"]))

    def test_equivalent_rewrite_binds_but_textual_baseline_rejects(self):
        candidate = contract(op("and", var("q"), var("p")), var("q"))
        gate = oracle_gate(self.safe, candidate, solve(candidate))
        self.assertTrue(gate["certificate_bound_to_original"])
        self.assertFalse(gate["textual_identity"])

    def test_600_random_solver_checker_agreements(self):
        rng = random.Random(6008)
        for n in (3, 4, 5):
            for _ in range(200):
                c = contract(random_expr(rng, list("pqrst"[:n]), 3),
                             random_expr(rng, list("pqrst"[:n]), 3), n)
                certificate = solve(c)
                self.assertTrue(verify(c, certificate)["valid"])
                self.assertEqual(certificate["verdict"], truth(c)["verdict"])
                witness = confirmed_counterexample(c)
                self.assertEqual(witness is None, certificate["verdict"] == "SAFE")


if __name__ == "__main__":
    unittest.main()
