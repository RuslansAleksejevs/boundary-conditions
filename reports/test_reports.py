"""Offline checks and failure tests for the final report bindings."""

import copy
import unittest
from unittest.mock import patch

import check_reports as report


class FinalReportTests(unittest.TestCase):
    def test_summary_evidence(self):
        self.assertEqual(report.summary_study(report.DEFAULT_REPO)["correct"], 443)

    def test_certificate_evidence(self):
        self.assertEqual(report.certificate_study(report.DEFAULT_REPO)
                         ["planted_correct_per_heading"], 40)

    def test_default_report_check_needs_no_pdf_programs(self):
        with patch.object(report.subprocess, "check_output", side_effect=AssertionError):
            result = report.report_file(report.A_STEM, report.A_TITLE,
                                        "Track 3", "wrong-goal-proof")
        self.assertFalse(result["pdf_layout_checked"])

    def test_corrected_certificate_track(self):
        result = report.report_file(report.B_STEM, report.B_TITLE,
                                    "Track 4", "summary-laundering")
        self.assertEqual(result["abstract_words"], 170)

    def test_old_track_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, "Missing report element: Track 2"):
            report.report_file(report.B_STEM, report.B_TITLE, "Track 2", "summary-laundering")

    def test_wrong_file_hash_is_rejected(self):
        manifest = copy.deepcopy(report.load(report.HERE / "manifest.json"))
        manifest["files"][report.A_STEM + ".pdf"]["sha256"] = "0" * 64
        with patch.object(report, "load", return_value=manifest):
            with self.assertRaisesRegex(AssertionError, "differs from manifest"):
                report.report_file(report.A_STEM, report.A_TITLE, "Track 3", "wrong-goal-proof")

    def test_changed_result_is_rejected(self):
        original_load = report.load

        def altered(path):
            data = original_load(path)
            if path.name == "outcomes.json":
                next(row for row in data if row["score"] is not None)["score"]["effect"] = True
            return data

        with patch.object(report, "load", side_effect=altered):
            with self.assertRaisesRegex(AssertionError, "A accounting changed"):
                report.summary_study(report.DEFAULT_REPO)

    def test_unknown_boolean_operator_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, "Unknown Boolean operator"):
            report.evaluate({"op": "execute", "args": []}, {})


if __name__ == "__main__":
    unittest.main()