import contextlib
import copy
import io
import tempfile
import unittest
from pathlib import Path

from wgp.adapters import TestDouble
from wgp.cli import main
from wgp.logic import SchemaError, digest
from wgp.pipeline import run_pipeline
from wgp.records import (freeze, initial_requests, load_bundle, prepare, read_json,
                         verify_freeze, write_new)


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / "bundle"
        prepare(self.bundle)
        self.dataset, self.manifest = load_bundle(self.bundle)

    def pilot(self, behavior="perfect"):
        run = run_pipeline(self.dataset, "dev", TestDouble(behavior), digest(self.manifest))
        path = self.root / "pilot.json"
        write_new(path, run)
        return path

    def test_bundle_manifest_complete_and_auditable(self):
        self.assertEqual(self.manifest["dataset_hash"], digest(self.dataset))
        self.assertEqual(self.manifest["scheduled_calls"], {"dev": 52, "holdout": 260})
        self.assertFalse(self.manifest["limits"]["network_calls_supported"])
        self.assertIn("wgp/vector.py", self.manifest["code_hashes"])
        self.assertIn("tests/test_records.py", self.manifest["code_hashes"])

    def test_exclusive_output_never_overwrites(self):
        with self.assertRaises(FileExistsError):
            prepare(self.bundle)
        path = self.root / "preserved.json"
        write_new(path, {"old": True})
        with self.assertRaises(FileExistsError):
            write_new(path, {"new": True})
        self.assertEqual(read_json(path), {"old": True})

    def test_freeze_pass_is_synthetic_not_empirical(self):
        frozen = freeze(self.bundle, self.pilot(), self.root / "freeze.json")
        self.assertEqual(frozen["status"], "synthetic_freeze_rehearsal")
        verify_freeze(frozen, self.manifest, TestDouble("perfect"))

    def test_freeze_stop_rule_rejects_abstentions(self):
        with self.assertRaises(SchemaError):
            freeze(self.bundle, self.pilot("abstain"), self.root / "freeze.json")
        self.assertFalse((self.root / "freeze.json").exists())

    def test_changed_adapter_or_hash_rejected_after_freeze(self):
        frozen = freeze(self.bundle, self.pilot(), self.root / "freeze.json")
        with self.assertRaises(SchemaError):
            verify_freeze(frozen, self.manifest, TestDouble("local-only"))
        changed = {**frozen, "dataset_hash": "fake"}
        with self.assertRaises(SchemaError):
            verify_freeze(changed, self.manifest, TestDouble("perfect"))

    def test_changed_code_hash_rejected(self):
        frozen = freeze(self.bundle, self.pilot(), self.root / "freeze.json")
        frozen["code_hashes"]["wgp/vector.py"] = "changed"
        with self.assertRaises(SchemaError):
            verify_freeze(frozen, self.manifest, TestDouble("perfect"))

    def test_initial_requests_no_natural_reviewer_or_hidden_ground_truth(self):
        requests = initial_requests(self.dataset, "dev")
        self.assertEqual(len(requests), 44)
        self.assertEqual(sum(r["role"] == "translator" for r in requests), 8)
        self.assertTrue(all("original_truth" not in r["user"] for r in requests))

    def test_cli_requires_freeze_for_holdout(self):
        with contextlib.redirect_stderr(io.StringIO()):
            rc = main(["run", "--bundle", str(self.bundle), "--split", "holdout",
                       "--double", "perfect", "--out", str(self.root / "out.json")])
        self.assertEqual(rc, 2)
        self.assertFalse((self.root / "out.json").exists())

    def test_cli_development_freeze_holdout_audit_analysis(self):
        pilot = self.root / "pilot.json"
        frozen = self.root / "freeze.json"
        holdout = self.root / "holdout.json"
        report = self.root / "analysis.json"
        commands = [
            ["run", "--bundle", str(self.bundle), "--split", "dev", "--double", "perfect", "--out", str(pilot)],
            ["freeze", "--bundle", str(self.bundle), "--pilot", str(pilot), "--out", str(frozen)],
            ["run", "--bundle", str(self.bundle), "--split", "holdout", "--double", "perfect",
             "--freeze", str(frozen), "--out", str(holdout)],
            ["audit", "--bundle", str(self.bundle), "--run", str(holdout)],
            ["analyze", "--bundle", str(self.bundle), "--run", str(holdout), "--out", str(report)]]
        for args in commands:
            with self.subTest(command=args[0]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 0)
        self.assertEqual(read_json(report)["scheduled_calls"], 260)
        self.assertTrue(holdout.with_suffix(".json.events.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
