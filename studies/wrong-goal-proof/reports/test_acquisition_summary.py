"""No-network accounting fixtures; no new task generation or observations."""

import copy
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from acquisition_summary import campaign_summary, known_total, receipt_timing, stage_summary


class AccountingTests(unittest.TestCase):
    def test_decimal_not_binary_sum(self):
        self.assertEqual(known_total(["0.1", "0.2"], monetary=True)["total"], "0.3")

    def test_unknown_is_not_an_exact_zero(self):
        result = known_total(["0.2", None], monetary=True)
        self.assertEqual(result["known_sum"], "0.2")
        self.assertEqual(result["unknown_attempts"], 1)
        self.assertIsNone(result["total"])

    def test_all_unknown_and_token_missingness(self):
        result = known_total([None, None])
        self.assertEqual((result["known_sum"], result["known_attempts"]), (0, 0))
        self.assertIsNone(result["total"])
        self.assertEqual(known_total([10, 20])["total"], 30)

    def test_unfinished_campaign_rejected_without_acquisition(self):
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "main must have ended"):
                campaign_summary(Path(directory))

    @staticmethod
    def fixtures():
        # These timestamps and amounts are invented unit-test data, not receipts.
        return [
            {"attempt_id": "fixture-1", "logical_id": "fixture-role", "http_status": 429,
             "started_at": "2026-01-01T00:00:00Z", "finished_at": "2026-01-01T00:00:01Z",
             "latency_seconds": 1.0, "payload": {"synthetic_fixture": True}},
            {"attempt_id": "fixture-2", "logical_id": "fixture-role", "http_status": 200,
             "started_at": "2026-01-01T00:01:01Z", "finished_at": "2026-01-01T00:01:03Z",
             "latency_seconds": 2.0, "payload": {"synthetic_fixture": True}},
        ]

    def test_retry_timing_and_exact_identity(self):
        result = receipt_timing(self.fixtures())
        self.assertEqual(result["minimum_attempt_start_spacing_seconds"], 61)
        self.assertEqual(result["latency_mean_seconds"], 1.5)
        self.assertEqual(result["technical_retries"], 1)
        retry = result["retry_pairs"][0]
        self.assertTrue(retry["identical_payload"])
        self.assertEqual(retry["delay_after_prior_finish_seconds"], 60)

    def test_different_payload_is_not_identical(self):
        receipts = copy.deepcopy(self.fixtures())
        receipts[1]["payload"]["synthetic_fixture"] = False
        self.assertFalse(receipt_timing(receipts)["retry_pairs"][0]["identical_payload"])

    def test_no_receipts_has_no_latency_estimate(self):
        result = receipt_timing([])
        self.assertIsNone(result["minimum_attempt_start_spacing_seconds"])
        self.assertIsNone(result["latency_mean_seconds"])
        self.assertIsNone(result["latency_max_seconds"])
        self.assertEqual(result["technical_retries"], 0)

    def test_different_roles_are_not_retries(self):
        receipts = self.fixtures()
        receipts[1]["logical_id"] = "fixture-other-role"
        self.assertEqual(receipt_timing(receipts)["technical_retries"], 0)


class SavedPilotAccountingTests(unittest.TestCase):
    """Replay already-published pilot metadata; no model or task generation."""

    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "results" / "live-pilot-2026-11-08"
        records = {name: json.loads((path / (name + ".json")).read_text())
                   for name in ("run", "manifest", "audit")}
        cls.summary = stage_summary(records["run"], records["manifest"], records["audit"])

    def test_saved_pilot_cost_and_separate_denominators(self):
        summary = self.summary
        self.assertEqual(summary["reported_api_cost_usd"]["total"], "0.39923650")
        self.assertEqual(summary["reported_api_cost_usd"]["known_attempts"], 51)
        self.assertEqual(summary["physical_attempts"], 51)
        self.assertEqual(summary["scheduled_roles"], 52)
        self.assertEqual(summary["logical_role_statuses"]["blocked_translation"], 1)
        self.assertEqual(summary["stage_wallet"]["unknown_charges"], 0)
        self.assertEqual(summary["stage_wallet"]["unsettled_reservations"], 0)

    def test_saved_pilot_pacing_usage_and_no_retries(self):
        summary = self.summary
        self.assertEqual(summary["technical_retries"], 0)
        self.assertEqual(summary["minimum_attempt_start_spacing_seconds"], 20.000618)
        self.assertEqual(summary["usage"]["input_tokens"]["total"], 42437)
        self.assertEqual(summary["usage"]["output_tokens"]["total"], 186636)
        self.assertEqual(len(summary["schema_failures"]), 1)


if __name__ == "__main__":
    unittest.main()