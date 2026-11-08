"""SSE and conservative billing fixtures only; no credential lookup or network."""

import copy
import io
import signal
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from test_live import fixture_config
from wgp.live_http import OpenRouterHTTP, interpret_receipt, visible_response
from wgp.logic import SchemaError, canonical
from wgp.stream import assemble, audit_stream, read_sse, wall_timeout


def chunks():
    return [
        {"id": "fixture-stream-id", "model": "qwen/qwen3.5-122b-a10b", "provider": "Alibaba",
         "choices": [{"index": 0, "delta": {"role": "assistant", "reasoning_content": "PRIVATE_REASONING_FIXTURE"}, "finish_reason": None}]},
        {"id": "fixture-stream-id", "model": "qwen/qwen3.5-122b-a10b", "provider": "Alibaba",
         "choices": [{"index": 0, "delta": {"content": '{"verdict":"SAFE",'}, "finish_reason": None}]},
        {"choices": [{"index": 0, "delta": {"content": '"witness":null}'}, "finish_reason": "stop"}]},
        {"choices": [], "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300,
                                   "completion_tokens_details": {"reasoning_tokens": 70}, "cost": 0.00001}},
    ]


def wire(events=None, done=True):
    events = chunks() if events is None else events
    text = ": harmless keepalive\n\n" + "".join("data: " + canonical(c) + "\n\n" for c in events)
    return (text + ("data: [DONE]\n\n" if done else "")).encode()


class HTTPFixture(io.BytesIO):
    status = 200
    headers = {"content-type": "text/event-stream; charset=utf-8", "x-request-id": "fixture-header-id"}


def acquire_fixture(data):
    # Literal test token; not an attached credential. The opener is replaced before send.
    client = OpenRouterHTTP("unit-test-no-secret", 2)
    client.opener = SimpleNamespace(open=lambda *args, **kwargs: HTTPFixture(data))
    return {**client.send({"fixture": True}), "transport_kind": "official_openrouter_http"}


class StreamTests(unittest.TestCase):
    def test_complete_visible_stream_is_reassembled_and_reasoning_discarded(self):
        receipt = acquire_fixture(wire())
        result = interpret_receipt(receipt, fixture_config())
        self.assertEqual(result["status"], "response")
        self.assertEqual(result["text"], '{"verdict":"SAFE","witness":null}')
        self.assertTrue(receipt["stream"]["done"])
        self.assertNotIn("PRIVATE_REASONING_FIXTURE", canonical(receipt))
        self.assertNotIn("reasoning_content", canonical(receipt))
        self.assertEqual(result["usage"]["reasoning_tokens"], 70)

    def test_conservative_charge_is_separate_from_discounted_api_cost(self):
        result = interpret_receipt(acquire_fixture(wire()), fixture_config())
        self.assertEqual(result["usage"]["cost_usd"], 0.00001)
        self.assertEqual(result["ledger_charge_usd"], "0.000135")

    def test_missing_billing_retains_full_unknown_reservation(self):
        data = chunks()
        data[-1]["usage"].pop("cost")
        result = interpret_receipt(acquire_fixture(wire(data)), fixture_config())
        self.assertEqual(result["status"], "response")
        self.assertIsNone(result["ledger_charge_usd"])
        self.assertIsNone(result["usage"]["cost_usd"])

    def test_interim_usage_before_finish_is_not_final_billing(self):
        data = chunks()
        data[2], data[3] = data[3], data[2]
        receipt = acquire_fixture(wire(data))
        result = interpret_receipt(receipt, fixture_config())
        self.assertTrue(result["fatal"])
        self.assertIsNone(result["ledger_charge_usd"])
        self.assertIsNone(result["usage"]["cost_usd"])

    def test_missing_done_finish_usage_or_identity_is_rejected(self):
        for defect in ("done", "finish", "usage", "provider", "role"):
            data = chunks()
            if defect == "finish":
                data[2]["choices"][0]["finish_reason"] = None
            elif defect == "usage":
                data.pop()
            elif defect == "provider":
                data[0].pop("provider")
                data[1].pop("provider")
            elif defect == "role":
                data[0]["choices"][0]["delta"].pop("role")
            receipt = acquire_fixture(wire(data, done=defect != "done"))
            result = interpret_receipt(receipt, fixture_config())
            with self.subTest(defect=defect):
                self.assertNotEqual(result["status"], "response")
                self.assertIsNone(result["ledger_charge_usd"])

    def test_midstream_identity_change_tool_call_and_duplicate_usage_rejected(self):
        for defect in ("id", "model", "provider", "tool", "usage"):
            data = chunks()
            if defect in ("id", "model", "provider"):
                data[1][defect] = "changed"
            elif defect == "tool":
                data[1]["choices"][0]["delta"]["tool_calls"] = [{"function": {"name": "not_allowed"}}]
            else:
                data.append(copy.deepcopy(data[-1]))
            with self.subTest(defect=defect), self.assertRaises(SchemaError):
                assemble(visible_response(data), True)

    def test_sse_wire_limit_and_malformed_json_fail_closed(self):
        with patch("wgp.stream.MAX_WIRE_BYTES", 100):
            result = interpret_receipt(acquire_fixture(wire()), fixture_config())
            self.assertIsNone(result["ledger_charge_usd"])
            self.assertTrue(result["fatal"])
        result = interpret_receipt(acquire_fixture(b'data: {"duplicate":1,"duplicate":2}\n\ndata: [DONE]\n\n'), fixture_config())
        self.assertTrue(result["fatal"])
        self.assertIsNone(result["ledger_charge_usd"])

    def test_reassembled_response_tampering_is_not_released_as_valid_billing(self):
        receipt = acquire_fixture(wire())
        receipt["response"]["choices"][0]["message"]["content"] = "changed"
        result = interpret_receipt(receipt, fixture_config())
        self.assertEqual(result["status"], "integrity_error")
        self.assertIsNone(result["ledger_charge_usd"])

    def test_late_content_after_finish_is_rejected(self):
        data = visible_response(chunks())
        data.append({"choices": [{"index": 0, "delta": {"content": "late"}, "finish_reason": None}]})
        with self.assertRaises(SchemaError):
            assemble(data, True)

    def test_total_context_violation_stops_without_releasing_uncertain_billing(self):
        data = chunks()
        data[-1]["usage"].update(prompt_tokens=150000, completion_tokens=150000, total_tokens=300000)
        config = fixture_config()
        result = interpret_receipt(acquire_fixture(wire(data)), config)
        self.assertTrue(result["fatal"])
        self.assertIsNone(result["ledger_charge_usd"])

    def test_literal_test_credential_echo_is_redacted_in_stream(self):
        data = chunks()
        data[1]["choices"][0]["delta"]["content"] = "unit-test-no-secret"
        receipt = acquire_fixture(wire(data))
        self.assertNotIn("unit-test-no-secret", canonical(receipt))
        self.assertIn("[REDACTED_CREDENTIAL]", canonical(receipt))

    def test_wall_timer_is_bounded_and_restored(self):
        previous = signal.getsignal(signal.SIGALRM)
        with self.assertRaises(TimeoutError):
            with wall_timeout(0.005):
                time.sleep(0.025)
        self.assertEqual(signal.getsignal(signal.SIGALRM), previous)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()