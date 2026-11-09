"""Publication-envelope fixtures only, not generated task/model observations."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from pilot_release import export_pilot, inventory, validate_subset, verify_pilot


PUBLIC_PILOT = Path(__file__).resolve().parents[1] / "results" / "live-pilot-2026-11-08"


def subset_fixture():
    groups = ["natural"] * 8 + ["fault"] * 8 + ["equivalent"] * 4
    return {"version": 1, "kind": "development_subset_not_full_dataset",
            "source_dataset_hash": "FICTIONAL-TEST-HASH",
            "cases": [{"split": "dev", "id": f"dev-FICTIONAL-{i:03d}", "group": group}
                      for i, group in enumerate(groups)]}


class PilotBoundaryTests(unittest.TestCase):
    def test_only_development_envelope_is_accepted(self):
        self.assertEqual(len(validate_subset(subset_fixture())), 20)

    def test_holdout_case_rejected(self):
        for field, value in (("split", "holdout"), ("id", "holdout-FICTIONAL-000")):
            subset = subset_fixture()
            subset["cases"][0][field] = value
            with self.assertRaisesRegex(ValueError, "held-out or foreign"):
                validate_subset(subset)

    def test_missing_duplicate_and_population_change_rejected(self):
        subset = subset_fixture()
        subset["cases"].pop()
        with self.assertRaises(ValueError):
            validate_subset(subset)
        subset = subset_fixture()
        subset["cases"][1]["id"] = subset["cases"][0]["id"]
        with self.assertRaises(ValueError):
            validate_subset(subset)
        subset = subset_fixture()
        subset["cases"][0]["group"] = "fault"
        with self.assertRaises(ValueError):
            validate_subset(subset)

    def test_started_main_prevents_pilot_only_export(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / "source", Path(directory) / "view"
            (source / "main").mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "unstarted main"):
                export_pilot(source, target)
            self.assertFalse(target.exists())


class SavedPilotReplayTests(unittest.TestCase):
    """Mutation tests of the released development view; never new observations."""

    def copied_view(self, directory):
        target = Path(directory) / "mutated-test-copy"
        shutil.copytree(PUBLIC_PILOT, target)
        return target

    def rewrite_with_consistent_inventory(self, view, name, value):
        (view / name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        record = json.loads((view / "EXPORT.json").read_text(encoding="utf-8"))
        record["files"] = inventory(view)
        (view / "EXPORT.json").write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    def test_saved_actual_pilot_replays_without_new_calls(self):
        result = verify_pilot(PUBLIC_PILOT)
        self.assertEqual((result["originals"], result["calls"], result["outcomes"]), (20, 52, 44))
        self.assertEqual(result["new_model_calls"], 0)
        self.assertFalse(result["full_acquisition_audit_reproduced"])
        self.assertFalse(result["dev_holdout_separation_reproduced"])

    def test_visible_answer_corruption_fails_even_after_hashes_are_updated(self):
        with tempfile.TemporaryDirectory() as directory:
            view = self.copied_view(directory)
            run = json.loads((view / "run.json").read_text(encoding="utf-8"))
            next(call for call in run["calls"] if call["status"] == "completed")["response_text"] = "FICTIONAL MUTATION: NOT JSON"
            self.rewrite_with_consistent_inventory(view, "run.json", run)
            with self.assertRaises(ValueError):
                verify_pilot(view)

    def test_aggregate_corruption_fails_even_after_hashes_are_updated(self):
        with tempfile.TemporaryDirectory() as directory:
            view = self.copied_view(directory)
            analysis = json.loads((view / "analysis.json").read_text(encoding="utf-8"))
            analysis["natural_unassessed_translations"] = 0
            self.rewrite_with_consistent_inventory(view, "analysis.json", analysis)
            with self.assertRaisesRegex(ValueError, "aggregate analysis"):
                verify_pilot(view)

    def test_full_dataset_name_cannot_be_added_to_the_view(self):
        with tempfile.TemporaryDirectory() as directory:
            view = self.copied_view(directory)
            (view / "dataset.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "full dataset"):
                verify_pilot(view)

    def test_changed_record_bytes_fail_the_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            view = self.copied_view(directory)
            (view / "analysis.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inventory"):
                verify_pilot(view)


if __name__ == "__main__":
    unittest.main()