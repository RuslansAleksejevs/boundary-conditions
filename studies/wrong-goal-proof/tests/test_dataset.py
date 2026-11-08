import copy
import unittest

from wgp.certificates import verify
from wgp.dataset import FAULTS, EQUIVALENTS, audit_dataset, make_dataset, skeleton
from wgp.logic import SchemaError, digest, render_contract
from wgp.vector import fidelity, signature, truth


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = make_dataset(6006)

    def test_planned_counts_and_families(self):
        for split, sizes in (("dev", (8, 8, 4)), ("holdout", (40, 40, 20))):
            cases = self.data["splits"][split]
            for group, expected in zip(("natural", "fault", "equivalent"), sizes):
                self.assertEqual(sum(c["group"] == group for c in cases), expected)
            for family in FAULTS:
                self.assertEqual(sum(c["family"] == family for c in cases), sizes[1] // 4)
            for family in EQUIVALENTS:
                self.assertEqual(sum(c["family"] == family for c in cases), sizes[2] // 4)

    def test_reproducible_generation(self):
        self.assertEqual(digest(self.data), digest(make_dataset(6006)))
        self.assertNotEqual(digest(self.data), digest(make_dataset(6007)))

    def test_disjoint_semantics_and_original_skeletons(self):
        all_sigs, shapes = [], []
        for split in ("dev", "holdout"):
            cases = self.data["splits"][split]
            all_sigs.append({signature(c[key]) for c in cases for key in ("original", "candidate")
                             if c[key] is not None})
            shapes.append({skeleton(c["original"]) for c in cases})
        self.assertFalse(all_sigs[0] & all_sigs[1])
        self.assertFalse(shapes[0] & shapes[1])

    def test_all_planted_faults_unsafe_original_safe_nonempty_candidate(self):
        for cases in self.data["splits"].values():
            for case in cases:
                if case["group"] != "fault":
                    continue
                self.assertEqual(truth(case["original"])["verdict"], "UNSAFE")
                self.assertEqual(truth(case["candidate"])["verdict"], "SAFE")
                self.assertGreater(truth(case["candidate"])["admissible_count"], 0)
                self.assertFalse(fidelity(case["original"], case["candidate"])["open_functions_equal"])
                self.assertTrue(verify(case["candidate"], case["certificate"])["valid"])

    def test_all_equivalent_controls_change_syntax_preserve_both_functions(self):
        for cases in self.data["splits"].values():
            for case in cases:
                if case["group"] == "equivalent":
                    self.assertNotEqual(case["original"], case["candidate"])
                    self.assertTrue(fidelity(case["original"], case["candidate"])["open_functions_equal"])
                    self.assertEqual(truth(case["original"])["verdict"], "SAFE")

    def test_natural_tasks_balanced_no_precomputed_translation(self):
        for split, cases in self.data["splits"].items():
            natural = [c for c in cases if c["group"] == "natural"]
            self.assertEqual(sum(truth(c["original"])["verdict"] == "SAFE" for c in natural), len(natural) // 2)
            self.assertTrue(all(c["candidate"] is None and c["certificate"] is None for c in natural))

    def test_each_family_changes_intended_field(self):
        for case in self.data["splits"]["holdout"]:
            if case["group"] != "fault":
                continue
            original, candidate = case["original"], case["candidate"]
            if case["family"] == "restrict_C":
                self.assertEqual(original["Q"], candidate["Q"])
                self.assertEqual(candidate["C"]["args"], [original["C"], original["Q"]])
            else:
                self.assertEqual(original["C"], candidate["C"])
                if case["family"] == "drop_conjunct":
                    self.assertEqual(candidate["Q"], original["Q"]["args"][0])
                elif case["family"] == "and_to_or":
                    self.assertEqual(candidate["Q"]["args"], original["Q"]["args"])
                    self.assertEqual(candidate["Q"]["op"], "or")
                else:
                    self.assertEqual(candidate["Q"]["args"], original["Q"]["args"][::-1])

    def test_audit_rejects_duplicate_ids_or_cases(self):
        data = copy.deepcopy(self.data)
        data["splits"]["dev"][1] = copy.deepcopy(data["splits"]["dev"][0])
        with self.assertRaises(SchemaError):
            audit_dataset(data)

    def test_audit_rejects_task_or_certificate_tampering(self):
        for kind in ("task", "certificate"):
            data = copy.deepcopy(self.data)
            case = next(c for c in data["splits"]["dev"] if c["group"] == "fault")
            if kind == "task":
                case["task"] += "\nAdditional instruction"
            else:
                case["certificate"]["rows"].pop()
            with self.assertRaises(SchemaError):
                audit_dataset(data)

    def test_audit_rejects_cross_split_semantic_duplicate(self):
        data = copy.deepcopy(self.data)
        source = next(c for c in data["splits"]["dev"] if c["family"] == "restrict_C")
        target = next(c for c in data["splits"]["holdout"] if c["family"] == "restrict_C")
        target.update({key: copy.deepcopy(source[key]) for key in ("original", "candidate", "task", "certificate")})
        with self.assertRaises(SchemaError):
            audit_dataset(data)

    def test_ten_additional_seeds(self):
        for seed in range(6100, 6110):
            self.assertTrue(audit_dataset(make_dataset(seed))["valid"])


if __name__ == "__main__":
    unittest.main()
