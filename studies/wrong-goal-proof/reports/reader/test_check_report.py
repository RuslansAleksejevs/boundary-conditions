"""No-network tests of reporting bindings, using the immutable public records."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_report as report


class ReaderReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = report.read(report.CAMPAIGN / "dataset.json")
        cls.saved_run = report.read(report.CAMPAIGN / "main/run.json")
        cls.derived = report.read(report.HERE / "report-data.json")

    def small_dataset(self, case_id):
        case = next(c for c in self.dataset["splits"]["holdout"] if c["id"] == case_id)
        return {"splits": {"holdout": [deepcopy(case)]}}

    def small_run(self, case_id):
        return {"calls": deepcopy([c for c in self.saved_run["calls"]
                                   if c["request"]["id"].startswith(case_id + ":")]),
                "outcomes": deepcopy([o for o in self.saved_run["outcomes"] if o["case_id"] == case_id])}

    def test_exact_examples_all_states_and_real_answers(self):
        for cid, failures in zip(report.EXAMPLES, (2, 0)):
            result = report.example(self.dataset, self.saved_run, cid)
            self.assertEqual(len(result["all_states"]), 16)
            self.assertEqual(result["original_admissible"], 8)
            self.assertEqual(result["candidate_admissible"], 8)
            self.assertEqual(result["original_failure_states"], failures)
            self.assertEqual(result["candidate_failure_states"], 0)
            self.assertEqual(set(result["answers"]), {"B", "N", "S"})

    def test_posthoc_shortest_rule_matches_declared_examples(self):
        report.check_selection(self.dataset)

    def test_wrong_displayed_formula_is_rejected(self):
        def wrong(cid, state):
            c, q, cp, qp = report.displayed_values(cid, state)
            return c, not q, cp, qp
        with self.assertRaisesRegex(ValueError, "printed interpretation"):
            report.example(self.dataset, self.saved_run, report.EXAMPLES[0], display=wrong)

    def test_wrong_certificate_row_is_rejected(self):
        data = self.small_dataset(report.EXAMPLES[0])
        data["splits"]["holdout"][0]["certificate"]["rows"][0]["Q"] = False
        with self.assertRaisesRegex(ValueError, "certificate is invalid"):
            report.example(data, self.saved_run, report.EXAMPLES[0])

    def test_duplicate_selected_source_is_rejected(self):
        data = self.small_dataset(report.EXAMPLES[0])
        data["splits"]["holdout"] *= 2
        with self.assertRaisesRegex(ValueError, "exactly one"):
            report.example(data, self.saved_run, report.EXAMPLES[0])

    def test_wrong_raw_response_quote_is_rejected(self):
        run = self.small_run(report.EXAMPLES[0])
        run["calls"][0]["response_text"] = '{"verdict":"SAFE","witness":null}'
        with self.assertRaisesRegex(ValueError, "answer/status binding"):
            report.example(self.dataset, run, report.EXAMPLES[0])

    def test_false_witness_is_rejected_even_with_matching_parsed_and_raw(self):
        cid = report.EXAMPLES[0]
        run = self.small_run(cid)
        for call in run["calls"]:
            if call["request"]["condition"] == "B":
                call["parsed"]["witness"]["p"] = True
                call["response_text"] = json.dumps(call["parsed"])
        for outcome in run["outcomes"]:
            if outcome["condition"] == "B":
                outcome["answer"]["witness"]["p"] = True
        with self.assertRaisesRegex(ValueError, "original witness is false"):
            report.example(self.dataset, run, cid)

    def test_source_pointers_resolve_to_exact_records(self):
        def pointer(value, path):
            for key in path.strip("/").split("/"):
                value = value[int(key)] if isinstance(value, list) else value[key]
            return value
        for item in self.derived["examples"]:
            self.assertEqual(pointer(self.dataset, item["source_map"]["dataset.json"]["original"]),
                             item["original"])
            for arm in ("B", "N", "S"):
                self.assertEqual(pointer(self.saved_run, item["source_map"]["main/run.json"][arm]["response_text"]),
                                 item["answers"][arm]["response_text"])

    def test_table_assets_are_exactly_generated_from_checked_data(self):
        for name, text in report.render_assets(self.derived).items():
            self.assertEqual((report.HERE / name).read_text(), text)
        natural = self.derived["main_outcomes"][0]
        self.assertEqual((natural["correct"], natural["scheduled"], natural["assessed"]), (36, 40, 36))
        self.assertEqual((natural["invalid_reviews"], natural["blocked_reviews"]), (1, 3))

    def test_preserved_file_hashes_and_corruption_detection(self):
        inventory = report.read(report.HERE / "preserved-files.json")
        self.assertEqual(report.verify_preserved(inventory), 91)
        broken = deepcopy(inventory)
        broken["files"]["reports/main/main-report.pdf"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "preserved file changed"):
            report.verify_preserved(broken)

    def test_printed_math_and_quote_bindings(self):
        report.check_document(self.derived)
        original = (report.HERE / "verified-but-what.tex").read_text()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "verified-but-what.tex"
            target.write_text(original.replace(report.PRINTED_MATH[0], "incorrect formula"))
            with patch.object(report, "HERE", Path(directory)):
                with self.assertRaisesRegex(ValueError, "printed formula"):
                    report.check_document(self.derived)

    def test_missing_outcomes_and_unknown_costs_are_not_zero_imputed(self):
        self.assertEqual(self.derived["natural_missingness_bounds"], [0.0, 0.1])
        self.assertEqual(self.derived["stages"][1]["unknown_cost_attempts"], 2)
        self.assertEqual(self.derived["unknown_holds_usd"], "1.22683392")
        self.assertEqual(self.derived["paired"]["primary_fault_S_minus_B"]["complete_pairs"], 40)
        self.assertGreater(self.derived["paired"]["primary_fault_S_minus_B"]["bounded_iid_hoeffding95"][1], 0.42)


if __name__ == "__main__":
    unittest.main()