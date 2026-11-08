"""Pure reporting tests; no inference, network or scientific fixtures."""

from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "report"))
from export_results import paired_svg, selected_traces, stage_cost, load_run


class ReportingTests(unittest.TestCase):
    def test_svg_preserves_nonzero_uncertainty_at_zero_difference(self):
        rows = [{"a": "S-P", "b": b, "difference_pp": 0,
                 "bounded_independent_cluster_95_ci_pp": [-42.95, 42.95],
                 "cluster_bootstrap_95_ci_pp": [0, 0]} for b in ("S-D", "E-P")]
        svg = paired_svg(rows)
        root = ElementTree.fromstring(svg)
        bounded = [node for node in root.iter() if node.get("stroke") == "#8ca6c4"]
        self.assertEqual(len(bounded), 2)
        self.assertTrue(all(float(n.get("x2")) > float(n.get("x1")) for n in bounded))
        self.assertIn("Shared templates", svg)

    def test_svg_missing_estimates_are_not_zeroes(self):
        row = {"a": "S-P", "b": "S-D", "difference_pp": None}
        svg = paired_svg([row])
        self.assertIn("No complete pairs", svg)
        self.assertNotIn("<circle", svg)

    def test_stage_cost_distinguishes_receipt_unknown_from_reconciliation(self):
        manifest = {"phase": "pilot", "seed": 1, "manifest_hash": "fixture", "code_revision": "fixture", "planned_requests": 108}
        run = {"calls": [{"cost_usd": None, "status": "transport_error", "latency_seconds": 2,
                          "acquisition": {"started_at_utc": "2026-01-01T00:00:00+00:00", "finished_at_utc": "2026-01-01T00:00:02+00:00"}}],
               "retries_used": 0, "stop_reason": "transport_error"}
        report = {"cost": {"token_usage": {}}, "audit": {"charged_or_reserved_campaign_usd": "0.61341696"}, "pilot_gate": {"passed": False}}
        before = deepcopy(run)
        result = stage_cost(manifest, run, report, Decimal("0.00541606"))
        self.assertEqual(result["accepted_receipt_cost_usd"], "0")
        self.assertEqual(result["unknown_receipt_cost_calls"], 1)
        self.assertEqual(result["separately_reconciled_stage_cost_usd"], "0.00541606")
        self.assertEqual(result["cumulative_charged_or_reserved_usd"], "0.61341696")
        self.assertEqual(before, run)

    def test_trace_selection_is_prespecified_and_stable(self):
        scenarios = [{"scenario_id": sid, "family": family, "attacked": attacked}
                     for sid, family, attacked in (("b", "f1", True), ("a", "f1", True), ("c", "f2", True), ("d", "f2", False))]
        rows = [{"scenario_id": s["scenario_id"], "condition": "S-P", "attacked": s["attacked"],
                 "score": {"effect": s["scenario_id"] == "b"}, "status": "fixture", "gate_replay": {}} for s in scenarios]
        run = {"summaries": [{"scenario_id": s["scenario_id"]} for s in scenarios], "rows": rows, "calls": []}
        traces = selected_traces({"scenarios": scenarios}, run)
        self.assertEqual([t["scenario"]["scenario_id"] for t in traces], ["a", "b", "c"])

    def test_reporting_cannot_relabel_a_test_fixture(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "manifest.json").write_text(json.dumps({"phase": "main", "acquisition_mode": "test_fixture"}))
            (root / "run.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "real acquisition"):
                load_run(root, "main")


if __name__ == "__main__":
    unittest.main()