"""HTTP-free operational amendment tests. Fixtures never qualify empirical gates."""

from copy import deepcopy
from pathlib import Path
import signal
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sl.continuation import (ContinuationRunner, STAGE, check_scientific_sources, effective_pilot_sources,
                             make_continuation_plan, validate_continuation_go, validate_plan)
from sl.live_run import LiveRunner, audit_live, live_gate, live_manifest
from sl.live_transport import BudgetStop, Ledger, PacedTransport, audit_pacing, safe_retry_after, wall_timeout
from sl.protocol import canonical, digest
from sl.runner import code_hashes
from test_live import FixtureTransport, config, go, response


class Clock:
    def __init__(self):
        self.now, self.waits = 0.0, []
    def clock(self):
        return self.now
    def sleep(self, seconds):
        self.waits.append(seconds)
        self.now += seconds


class InterruptedFixture(FixtureTransport):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.attempts = 0
    def send(self, payload):
        self.attempts += 1
        if self.attempts in {1, 10, 20, 30, 40, 57, 58, 59}:
            record = response()
            record.update(http_status=429, visible_response=None, technical_error="http_429", retryable=True)
            return record
        return super().send(payload)


def interrupted_parent(ledger):
    cfg = ledger.config
    original = live_manifest(cfg, "pilot", 2026110801, fixture=True)
    first = LiveRunner(original, FixtureTransport(cfg, fail=True), ledger, go(cfg)).run()
    pilot = {"manifest": original, "gate": live_gate(original, first), "run_hash": digest(first)}
    repaired = live_manifest(cfg, "pilot_repair", 2026110830, pilot=pilot,
                             repair_reason="HTTP-free interface fixture, not an actual correction", fixture=True)
    parent = LiveRunner(repaired, InterruptedFixture(cfg), ledger, go(cfg)).run()
    return repaired, parent


def continued_fixture(fail=False, over_limit=False):
    cfg, clock = config(), Clock()
    with tempfile.TemporaryDirectory() as tmp, patch("sl.live_run.time.sleep"), patch("sl.live_transport.time.monotonic", side_effect=clock.clock):
        ledger = Ledger(Path(tmp) / "ledger.jsonl", cfg, create=True)
        manifest, parent = interrupted_parent(ledger)
        plan = make_continuation_plan(manifest, parent, fixture=True)
        approval = {**go(cfg), "continuation_plan_hash": plan["plan_hash"], "provider_route_exclusive": True}
        class OverLimit(FixtureTransport):
            def send(self, payload):
                record = super().send(payload)
                record.update(http_status=429, technical_error="http_429", retry_after_seconds="301")
                return record
        backend = OverLimit(cfg, fail=True) if over_limit else FixtureTransport(cfg, fail=fail)
        backend.responses = 10000
        with patch("sl.live_transport.time.sleep", side_effect=clock.sleep):
            composite = ContinuationRunner(manifest, parent, plan, PacedTransport(backend), ledger, approval).run()
        return manifest, parent, plan, composite, clock


class ContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.parent, cls.plan, cls.composite, cls.clock = continued_fixture()

    def test_exact_suffix_and_no_resampling(self):
        self.assertEqual(len(self.parent["calls"]), 59)
        self.assertEqual(len(self.plan["remaining_call_ids"]), 54)
        self.assertEqual(len(self.composite["calls"]), 113)
        self.assertEqual(self.composite["calls"][:59], self.parent["calls"])
        self.assertEqual(self.composite["retries_used"], 5)
        self.assertTrue(all(c["attempt"] == 0 for c in self.composite["calls"][59:]))
        self.assertFalse({c["call_id"] for c in self.parent["calls"]} & {c["call_id"] for c in self.composite["calls"][59:]})
        self.assertTrue(audit_live(self.manifest, self.composite)["passed"])

    def test_original_run_and_gate_remain_failed(self):
        self.assertEqual(self.parent["stop_reason"], "three_consecutive_failed_logical_transports")
        self.assertFalse(live_gate(self.manifest, self.parent)["passed"])
        self.assertEqual(self.composite["continuation"]["parent_run"], self.parent)
        self.assertTrue(live_gate(self.manifest, self.composite)["interface_thresholds_pass"])
        self.assertFalse(live_gate(self.manifest, self.composite)["passed"])

    def test_existing_outcome_cannot_be_rewritten(self):
        changed = deepcopy(self.composite)
        changed["rows"][0]["status"] = "fabricated"
        with self.assertRaisesRegex(ValueError, "previously attempted"):
            audit_live(self.manifest, changed)

    def test_parent_call_and_ledger_are_immutable(self):
        for field in ("calls", "ledger"):
            changed = deepcopy(self.composite)
            changed[field][0]["injected"] = True
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "rewrote old"):
                audit_live(self.manifest, changed)

    def test_remaining_ids_cannot_include_an_attempted_role(self):
        changed = deepcopy(self.plan)
        changed["remaining_call_ids"][0] = self.parent["calls"][0]["call_id"]
        changed["remaining_call_ids_hash"] = digest(changed["remaining_call_ids"])
        changed["plan_hash"] = digest({k: v for k, v in changed.items() if k != "plan_hash"})
        with self.assertRaisesRegex(ValueError, "untouched suffix"):
            validate_plan(changed, self.manifest, self.parent)

    def test_scientific_modules_cannot_change(self):
        changed = deepcopy(self.plan)
        changed["code_hashes"]["sl/data.py"] = "changed"
        changed["plan_hash"] = digest({k: v for k, v in changed.items() if k != "plan_hash"})
        with self.assertRaisesRegex(ValueError, "scientific source"):
            validate_plan(changed, self.manifest, self.parent, check_code=False)

    def test_preserved_function_hashes_and_effective_sources(self):
        check_scientific_sources(self.plan["original_code_hashes"], code_hashes())
        self.assertEqual(effective_pilot_sources(self.manifest, self.composite), self.plan["code_hashes"])

    def test_new_go_must_bind_amendment_and_exclusive_route(self):
        approval = go(config())
        with self.assertRaisesRegex(ValueError, "explicitly bind"):
            validate_continuation_go(approval, self.plan, config())
        approval.update(continuation_plan_hash=self.plan["plan_hash"], provider_route_exclusive=True)
        validate_continuation_go(approval, self.plan, config())
        approval["continuation_plan_hash"] = "other"
        with self.assertRaisesRegex(ValueError, "explicitly bind"):
            validate_continuation_go(approval, self.plan, config())

    def test_pacing_audited_and_waits_bounded(self):
        self.assertTrue(self.clock.waits)
        self.assertTrue(all(0 < seconds <= 30 for seconds in self.clock.waits))
        changed = deepcopy(self.composite)
        changed["calls"][60]["acquisition"]["paced_attempt_started_monotonic_seconds"] = 1
        with self.assertRaisesRegex(ValueError, "spacing"):
            audit_live(self.manifest, changed)

    def test_continuation_has_no_new_retries_and_retains_outage_circuit(self):
        manifest, parent, plan, composite, _ = continued_fixture(fail=True)
        self.assertEqual(len(composite["calls"]), 62)
        self.assertEqual(composite["retries_used"], 5)
        self.assertEqual(composite["stop_reason"], "three_consecutive_failed_logical_transports")
        self.assertTrue(audit_live(manifest, composite)["passed"])
        self.assertFalse(live_gate(manifest, composite)["passed"])

    def test_second_continuation_cannot_be_planned(self):
        with self.assertRaisesRegex(ValueError, "only the interrupted"):
            make_continuation_plan(self.manifest, self.composite, fixture=True)

    def test_over_limit_retry_after_halts_without_using_a_retry(self):
        manifest, parent, plan, composite, _ = continued_fixture(over_limit=True)
        self.assertEqual(len(composite["calls"]), 60)
        self.assertEqual(composite["retries_used"], 5)
        self.assertEqual(composite["stop_reason"], "retry_after_over_300_seconds")
        self.assertTrue(audit_live(manifest, composite)["passed"])

    def test_continuation_stage_requires_exact_ledger_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger", config(), create=True)
            with self.assertRaisesRegex(ValueError, "exact immutable parent"):
                ledger.start_stage(STAGE, "plan")

    def test_wallet_rejects_new_retries_phase_overrun_and_second_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture-wallet.jsonl"
            path.write_text("".join(canonical(e) + "\n" for e in self.parent["ledger"]))
            ledger = Ledger(path, config())
            parent = {"manifest_hash": self.manifest["manifest_hash"], "run_hash": digest(self.parent),
                      "ledger_tail_hash": self.parent["ledger"][-1]["record_hash"]}
            ledger.start_stage(STAGE, self.plan["plan_hash"], parent=parent)
            with self.assertRaisesRegex(BudgetStop, "no implicit"):
                ledger.start_stage(STAGE, self.plan["plan_hash"], parent=parent)
            with self.assertRaisesRegex(BudgetStop, "cannot add retries"):
                ledger.reserve("pilot_repair/fixture/1", STAGE, retry=True)
            for call_id in self.plan["remaining_call_ids"]:
                attempt_id = "pilot_repair/" + call_id + "/0"
                ledger.reserve(attempt_id, STAGE)
                ledger.settle(attempt_id, "0.00001", "completed")
            with self.assertRaisesRegex(BudgetStop, "113-attempt"):
                ledger.reserve("pilot_repair/unplanned/0", STAGE)

    def test_unknown_stage_cannot_poison_wallet(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "fixture-wallet", config(), create=True)
            before = ledger.snapshot()
            with self.assertRaisesRegex(BudgetStop, "explicitly started"):
                ledger.reserve("anything", STAGE)
            self.assertEqual(ledger.snapshot(), before)

    def test_gate_and_limit_edits_are_rejected_even_if_plan_rehashed(self):
        for field, value in (("new_retries", 1), ("combined_repair_attempt_cap", 114),
                             ("additional_valid_roles_needed", 0), ("minimum_start_spacing_seconds", 1)):
            changed = deepcopy(self.plan)
            changed[field] = value
            changed["plan_hash"] = digest({k: v for k, v in changed.items() if k != "plan_hash"})
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_plan(changed, self.manifest, self.parent)


class WallTimerTests(unittest.TestCase):
    def test_total_timer_interrupts_a_slow_dripped_line(self):
        old = signal.getsignal(signal.SIGALRM)
        with self.assertRaises(TimeoutError):
            with wall_timeout(0.03):
                for _ in range(50):
                    time.sleep(0.01)
        self.assertEqual(signal.getsignal(signal.SIGALRM), old)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))


class PacingPolicyTests(unittest.TestCase):
    def test_retry_after_normalization_never_retains_arbitrary_headers(self):
        from datetime import datetime, timezone
        self.assertEqual(safe_retry_after(" 00090 "), "90")
        self.assertEqual(safe_retry_after("Sun, 08 Nov 2026 20:02:01 GMT",
                                        datetime(2026, 11, 8, 20, 0, tzinfo=timezone.utc)), "121")
        for raw in ("DO_NOT_RETAIN_SECRET", "-1", "1" * 129, None, "invalid-date"):
            self.assertIsNone(safe_retry_after(raw))

    def test_429_wait_is_before_next_attempt_not_an_extra_retry(self):
        for delay, expected in ((None, 60), ("0", 60), ("90", 90), ("300", 300)):
            clock = Clock()
            class Backend:
                config = {}
                def __init__(self): self.calls = 0
                def send(self, payload):
                    self.calls += 1
                    return {"http_status": 429 if self.calls == 1 else 200, "retry_after_seconds": delay}
            backend = Backend()
            with patch("sl.live_transport.time.monotonic", side_effect=clock.clock), patch("sl.live_transport.time.sleep", side_effect=clock.sleep):
                pacer = PacedTransport(backend)
                first = pacer.send({})
                second = pacer.send({})
            with self.subTest(delay=delay):
                self.assertEqual(backend.calls, 2)
                self.assertEqual(first["paced_attempt_started_monotonic_seconds"], 20)
                self.assertEqual(second["paced_attempt_started_monotonic_seconds"], 20 + expected)
                self.assertTrue(all(seconds <= 30 for seconds in clock.waits))
                audit_pacing([{"acquisition": first}, {"acquisition": second}], None)

    def test_over_limit_blocks_the_pacer_and_requires_an_explicit_stop(self):
        clock = Clock()
        class Backend:
            config = {}
            def send(self, payload): return {"http_status": 429, "retry_after_seconds": "301"}
        with patch("sl.live_transport.time.monotonic", side_effect=clock.clock), patch("sl.live_transport.time.sleep", side_effect=clock.sleep):
            pacer = PacedTransport(Backend())
            first = pacer.send({})
            with self.assertRaisesRegex(ValueError, "remain stopped"):
                pacer.send({})
        audit_pacing([{"acquisition": first}], "retry_after_over_300_seconds")
        with self.assertRaisesRegex(ValueError, "halt"):
            audit_pacing([{"acquisition": first}], None)

    def test_timer_cleanup_on_arbitrary_error(self):
        old = signal.getsignal(signal.SIGALRM)
        with self.assertRaises(RuntimeError):
            with wall_timeout(1):
                raise RuntimeError("fixture")
        self.assertEqual(signal.getsignal(signal.SIGALRM), old)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()