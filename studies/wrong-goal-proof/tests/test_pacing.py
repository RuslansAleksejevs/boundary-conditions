"""Prospective pacing tests with virtual clocks and local HTTP doubles only."""

import io
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from test_live import fixture_config
from wgp.live_http import OpenRouterHTTP, interpret_receipt
from wgp.logic import SchemaError, canonical
from wgp.pacing import Pacer, cooldown, safe_error_envelope, safe_retry_after


class FakeClock:
    def __init__(self):
        self.now, self.sleeps = 0.0, []

    def clock(self):
        return self.now

    def sleep(self, delay):
        self.sleeps.append(delay)
        self.now += delay


class ErrorFixture(io.BytesIO):
    status = 429

    def __init__(self, retry_after):
        super().__init__(canonical({"error": {"code": 429, "message": "NEVER_PERSIST_RAW_BODY",
            "metadata": {"raw": "NEVER_PERSIST_RAW_BODY", "limit_source": "provider"}}}).encode())
        self.headers = {"retry-after": retry_after, "authorization": "NEVER_PERSIST_RAW_HEADER"}


class PacingTests(unittest.TestCase):
    def test_starts_are_twenty_seconds_apart_but_slow_calls_add_no_delay(self):
        clock = FakeClock()
        pacer = Pacer(clock.clock, clock.sleep)
        self.assertEqual(pacer.wait_before_start(), 0)
        clock.now += 7
        self.assertEqual(pacer.wait_before_start(), 20)
        clock.now += 25
        self.assertEqual(pacer.wait_before_start(), 45)
        self.assertEqual(clock.sleeps, [13])

    def test_429_waits_at_least_sixty_seconds_from_response_end(self):
        for value in (None, "invalid", "0", "2", "60", "120", "300"):
            clock = FakeClock()
            pacer = Pacer(clock.clock, clock.sleep)
            pacer.wait_before_start()
            clock.now += 5
            headers = {} if value is None else {"retry-after": value}
            pacer.after_response(429, headers)
            self.assertEqual(pacer.wait_before_start(), 5 + cooldown(headers))
            self.assertTrue(all(0 < delay <= 30 for delay in clock.sleeps))

    def test_long_retry_after_stops_instead_of_truncating_or_retrying(self):
        clock = FakeClock()
        pacer = Pacer(clock.clock, clock.sleep)
        pacer.wait_before_start()
        pacer.after_response(429, {"retry-after": "301"})
        with self.assertRaises(SchemaError):
            pacer.wait_before_start()
        self.assertEqual(clock.sleeps, [])

    def test_retry_after_dates_round_up_and_untrusted_values_are_not_retained(self):
        now = datetime(2026, 11, 8, 20, 0, 0, 500000, tzinfo=timezone.utc)
        self.assertEqual(safe_retry_after("Sun, 08 Nov 2026 20:01:01 GMT", now), "61")
        self.assertEqual(safe_retry_after("Sun, 08 Nov 2026 19:00:00 GMT", now), "0")
        self.assertEqual(safe_retry_after("  00120  ", now), "120")
        for value in (None, 60, "-1", "nan", "1.5", "١٢", "PRIVATE_RAW_HEADER", "x" * 129):
            with self.subTest(value=value):
                self.assertIsNone(safe_retry_after(value, now))

    def test_new_stage_has_conservative_monotonic_spacing(self):
        clock = FakeClock()
        pacer = Pacer(clock.clock, clock.sleep)
        pacer.after_prior_stage({"http_status": 200, "headers": {}})
        self.assertEqual(pacer.wait_before_start(), 20)
        pacer.after_prior_stage({"http_status": 429, "headers": {"retry-after": "90"}})
        self.assertEqual(pacer.wait_before_start(), 110)
        self.assertTrue(all(delay <= 30 for delay in clock.sleeps))

    def test_error_envelope_keeps_only_allowlisted_diagnostics(self):
        body = {"error": {"code": 429, "message": "PRIVATE", "limit_source": "provider",
                          "reason": "PRIVATE", "metadata": {"raw": "PRIVATE"}}}
        self.assertEqual(safe_error_envelope(body), {"error": {"code": 429, "limit_source": "provider"}})
        self.assertEqual(safe_error_envelope({"error": {"code": "PRIVATE"}}), {"error": {}})

    def test_http_429_diagnostics_and_long_retry_classification(self):
        for value, retryable in (("60", True), ("301", False), ("PRIVATE_RAW_HEADER", True)):
            client = OpenRouterHTTP("unit-test-no-secret", 2)
            clock = FakeClock()
            client.pacer = Pacer(clock.clock, clock.sleep)
            client.opener = SimpleNamespace(open=lambda *a, **kw: ErrorFixture(value))
            receipt = client.send({"fixture": True})
            result = interpret_receipt(receipt, fixture_config())
            with self.subTest(value=value):
                self.assertEqual(result["retryable"], retryable)
                self.assertEqual(result["fatal"], not retryable)
                self.assertIsNone(result["ledger_charge_usd"])
                self.assertEqual(receipt["response"], {"error": {"code": 429, "limit_source": "provider"}})
                self.assertNotIn("NEVER_PERSIST", canonical(receipt))
                self.assertNotIn("PRIVATE_RAW_HEADER", canonical(receipt))
                if retryable:
                    client.send({"fixture": True})
                    self.assertEqual(clock.now, 60)


if __name__ == "__main__":
    unittest.main()