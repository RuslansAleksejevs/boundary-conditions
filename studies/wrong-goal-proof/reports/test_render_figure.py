"""Presentation-only fabricated counts: never experimental model evidence."""

import copy
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from render_figure import render


def fabricated_analysis():
    rate = {"numerator": 0, "denominator": 40, "estimate": 0., "wilson95": [0., .09]}
    correct = {"numerator": 20, "denominator": 20, "estimate": 1., "wilson95": [.84, 1.]}
    outcome = {"observed_false_safe_all_scheduled": rate, "correct_completion": correct,
               "full_sample_false_safe_bounds": [0., 0.]}
    pair = {"difference": 0., "bootstrap95": [0., 0.], "bounded_iid_hoeffding95": [-.43, .43],
            "complete_pairs": 40, "scheduled_pairs": 40}
    return {"mode": "live_model_acquisition", "split": "holdout", "acquisition_audit": {"valid": True},
            "configuration": {"model": "FICTIONAL-RENDERER-UNIT-TEST", "provider_response_name": "NO-NETWORK"},
            "groups": {g: {arm: copy.deepcopy(outcome) for arm in ("B", "N", "S")}
                       for g in ("fault", "equivalent", "natural")},
            "primary_fault_S_minus_B": copy.deepcopy(pair), "secondary_fault_N_minus_B": copy.deepcopy(pair),
            "natural_drift_among_valid_translations": copy.deepcopy(rate)}


class FigureTests(unittest.TestCase):
    def test_refuses_test_double_label_and_missing_audit(self):
        for key, value in (("mode", "synthetic_test_double"), ("acquisition_audit", {}), ("split", "other")):
            data = fabricated_analysis()
            data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                render(data)

    def test_svg_is_valid_and_pdf_has_cross_reference_and_exact_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "FICTIONAL-renderer-test"
            render(fabricated_analysis()).write(stem)
            ET.parse(str(stem) + ".svg")
            pdf = Path(str(stem) + ".pdf").read_bytes()
            self.assertTrue(pdf.startswith(b"%PDF-1.4"))
            self.assertIn(b"(0/40)", pdf)
            self.assertIn(b"(20/20)", pdf)
            self.assertIn(b"(40/40 complete pairs)", pdf)
            self.assertTrue(pdf.endswith(b"%%EOF\n"))
            offset = int(pdf.split(b"startxref\n")[1].splitlines()[0])
            self.assertEqual(pdf[offset:offset+5], b"xref\n")
            with self.assertRaises(FileExistsError):
                render(fabricated_analysis()).write(stem)

    def test_pilot_is_explicitly_not_confirmatory(self):
        data = fabricated_analysis()
        data["split"] = "dev"
        self.assertIn("Development pilot (not confirmatory)", "".join(render(data).svg))

    def test_missing_pairs_and_unassessed_faults_remain_visible(self):
        data = fabricated_analysis()
        data["primary_fault_S_minus_B"].update(difference=None, complete_pairs=0)
        for arm in ("B", "N", "S"):
            outcome = data["groups"]["fault"][arm]
            outcome["observed_false_safe_all_scheduled"]["wilson95"] = None
            outcome["full_sample_false_safe_bounds"] = [0., .5]
        result = render(data)
        self.assertIn("0/40 complete pairs", "".join(result.svg))
        self.assertIn("missingness bounds", "".join(result.svg))


if __name__ == "__main__":
    unittest.main()