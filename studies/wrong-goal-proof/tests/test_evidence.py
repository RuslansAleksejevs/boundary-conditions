import copy
import unittest

from wgp.adapters import TestDouble
from wgp.dataset import make_dataset
from wgp.evidence import export_evidence, verify_evidence
from wgp.logic import SchemaError
from wgp.pipeline import run_pipeline


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = make_dataset()
        run = run_pipeline(data, "dev", TestDouble("local-only"), "fixture-manifest")
        cls.packet = export_evidence(data, run)

    def test_all_false_guarantees_independently_verifiable(self):
        result = verify_evidence(self.packet)
        self.assertEqual(result["cases"], 8)
        self.assertEqual(result["independently_confirmed_false_guarantees"], 24)
        self.assertFalse(result["provenance_authenticated"])

    def test_reject_false_witness(self):
        packet = copy.deepcopy(self.packet)
        packet["cases"][0]["evidence"]["witness"] = {"p": "false"}
        with self.assertRaises(SchemaError):
            verify_evidence(packet)

    def test_reject_certificate_or_hash_tampering(self):
        for part in ("certificate", "hash"):
            packet = copy.deepcopy(self.packet)
            if part == "certificate":
                packet["cases"][0]["certificate"]["rows"].pop()
            else:
                packet["cases"][0]["evidence"]["candidate_hash"] = "forged"
            with self.subTest(part=part), self.assertRaises(SchemaError):
                verify_evidence(packet)

    def test_reject_duplicate_case_and_non_safe_claim(self):
        packet = copy.deepcopy(self.packet)
        packet["cases"][1] = packet["cases"][0]
        with self.assertRaises(SchemaError):
            verify_evidence(packet)
        packet = copy.deepcopy(self.packet)
        packet["cases"][0]["answers"]["B"] = {"verdict": "UNRESOLVED", "witness": None}
        with self.assertRaises(SchemaError):
            verify_evidence(packet)


if __name__ == "__main__":
    unittest.main()
