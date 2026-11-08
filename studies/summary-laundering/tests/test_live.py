"""Targeted live-contract tests. HTTP is never contacted by these fixtures."""

from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import json
import io
from types import SimpleNamespace
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sl.analysis import analyze
from sl.backends import TestDouble
from sl.data import generate
from sl.live_run import LiveRunner, audit_live, check_fixture_separation, fresh_cases, live_gate, live_manifest, validate_live_manifest, verify_pilot_binding
from sl.live_transport import (
    BudgetStop, ENDPOINT, Ledger, NoRedirect, OpenRouterTransport, assemble_stream, audit_ledger, inspect_response,
    read_sse, reservation, utc_now, validate_config, validate_go, visible_envelope, visible_stream_event, wire_request,
)
from sl.protocol import digest
from sl.runner import code_hashes


def config():
    # A local fixture, NOT the approved acquisition configuration.
    return {
        "schema_version": 2, "model": "qwen/qwen3.5-122b-a10b", "provider_slug": "alibaba",
        "response_provider": "Alibaba", "temperature": 0.6, "top_p": 0.95, "reasoning_enabled": True, "stream": True,
        "max_tokens": 8192, "context_tokens": 262144, "output_reservation_tokens": 262144,
        "input_price_per_million": "0.26", "output_price_per_million": "2.08", "request_price_usd": "0",
        "price_source": "https://openrouter.ai/api/v1/models/qwen/qwen3.5-122b-a10b/endpoints",
        "price_as_of": "fixture-only", "data_collection": "deny", "timeout_seconds": 180,
        "max_request_utf8_bytes": 16000, "max_response_utf8_bytes": 8_000_000,
        "max_summary_utf8_bytes": 8000, "budget_usd": "30", "max_attempts": 788,
        "max_technical_retries": 32, "max_pilot_repeats": 1,
        "version_pin_status": "fixture; served weights not pinned",
    }


def go(cfg):
    return {"go": True, "study": "summary-laundering", "configuration_hash": digest(cfg),
            "code_hashes_hash": digest(code_hashes()),
            "budget_usd": cfg["budget_usd"], "max_attempts": cfg["max_attempts"],
            "approved_at_utc": "fixture-only", "authorization_reference": "UNIT_TEST_NOT_AUTHORIZATION"}


def response(text="visible", *, finish="stop", provider="Alibaba", cost=0.000468, generation_id="fixture-response"):
    now = utc_now()
    raw = {"id": generation_id, "model": "qwen/qwen3.5-122b-a10b", "provider": provider,
           "usage": {"prompt_tokens": 1000, "completion_tokens": 100, "total_tokens": 1100, "cost": cost,
                     "completion_tokens_details": {"reasoning_tokens": 30},
                     "prompt_tokens_details": {"cached_tokens": 0}},
           "choices": [{"index": 0, "finish_reason": finish,
                        "message": {"role": "assistant", "content": text, "reasoning": "never log this"}}]}
    return {"endpoint": ENDPOINT, "started_at_utc": now, "finished_at_utc": now,
            "http_status": 200, "request_id": "fixture-id", "server_date": None,
            "raw_body_sha256": "0" * 64, "visible_response": visible_envelope(raw),
            "technical_error": None, "retryable": False, "latency_seconds": 0.001}


class FixtureTransport:
    kind = "openrouter_live"

    def __init__(self, cfg, fail=False):
        self.config, self.fail = cfg, fail
        self.double = TestDouble("scripted")
        self.responses = 0

    def send(self, payload):
        if self.fail:
            result = response()
            result.update(http_status=503, visible_response=None, technical_error="http_503", retryable=True)
            return result
        role = "summarizer" if "Summarize the untrusted record" in payload["messages"][0]["content"] else "executor"
        result = self.double.complete({"role": role, "messages": payload["messages"]}, {}, "fixture")
        self.responses += 1
        return response(result.text, generation_id=f"fixture-response-{self.responses}")


def fixture_run(fail=False):
    cfg = config()
    manifest = live_manifest(cfg, "pilot", 2026110801, fixture=True)
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Ledger(Path(tmp) / "wallet.jsonl", cfg, create=True)
        with patch("sl.live_run.time.sleep"):
            run = LiveRunner(manifest, FixtureTransport(cfg, fail), ledger, go(cfg)).run()
    return manifest, run


def stream_frames():
    body = response()["visible_response"]
    base = {key: body[key] for key in ("id", "model", "provider", "created")}
    return [
        {**base, "choices": [{"index": 0, "delta": {"role": "assistant", "reasoning_content": "HIDDEN_FIXTURE_REASONING"}, "finish_reason": None}]},
        {**base, "choices": [{"index": 0, "delta": {"content": "vis"}, "finish_reason": None}]},
        {**base, "choices": [{"index": 0, "delta": {"content": "ible"}, "finish_reason": "stop"}]},
        {**base, "choices": [], "usage": body["usage"]},
    ]


def stream_bytes(frames=None, done=True):
    frames = stream_frames() if frames is None else frames
    body = b": keepalive\n\n" + b"".join(b"data: " + json.dumps(frame, ensure_ascii=False).encode() + b"\n\n" for frame in frames)
    return body + (b"data: [DONE]\n\n" if done else b"")


def stream_record():
    return {"stream_events": [], "stream_done": False, "visible_response": None}


class TransportTests(unittest.TestCase):
    def test_model_and_spending_constraints(self):
        for key, value in (("budget_usd", "50"), ("max_attempts", 789), ("max_technical_retries", 33),
                           ("model", "openai/gpt-oss-120b"), ("provider_slug", "together"),
                           ("top_p", 0), ("reasoning_enabled", "medium"), ("context_tokens", 131072),
                           ("request_price_usd", "0.01"), ("timeout_seconds", 181)):
            cfg = config()
            cfg[key] = value
            with self.assertRaises(ValueError):
                validate_config(cfg)

    def test_go_required_before_environment_access(self):
        with patch("sl.live_transport.os.environ.get", side_effect=AssertionError("credential lookup")):
            with self.assertRaises(ValueError):
                OpenRouterTransport(config(), {"go": False})

    def test_go_binds_configuration(self):
        cfg = config()
        approval = go(cfg)
        cfg["temperature"] = 1
        with self.assertRaises(ValueError):
            validate_go(approval, cfg)

    def test_go_binds_reviewed_code(self):
        cfg = config()
        approval = go(cfg)
        approval["code_hashes_hash"] = "not-reviewed"
        with self.assertRaises(ValueError):
            validate_go(approval, cfg)

    def test_https_serialization_and_no_credential_logging(self):
        cfg = config()
        class HTTPResponse:
            status = 200
            headers = {"x-request-id": "test-id", "date": "test-date", "content-type": "text/event-stream"}
            def __init__(self):
                self.data = io.BytesIO(stream_bytes())
                self.fp = SimpleNamespace(raw=SimpleNamespace(_sock=SimpleNamespace(settimeout=lambda seconds: None)))
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def readline(self, limit):
                return self.data.readline(limit)
        with patch("sl.live_transport.os.environ.get", return_value="UNIT_TEST_FAKE_KEY"), patch("sl.live_transport.request.build_opener") as builder:
            builder.return_value.open.return_value = HTTPResponse()
            transport = OpenRouterTransport(cfg, go(cfg))
            payload = wire_request([], cfg)
            record = transport.send(payload)
            sent = builder.return_value.open.call_args.args[0]
            self.assertEqual(sent.full_url, ENDPOINT)
            self.assertEqual(json.loads(sent.data), payload)
            self.assertNotIn("UNIT_TEST_FAKE_KEY", str(record))
            self.assertNotIn("HIDDEN_FIXTURE_REASONING", str(record))
            self.assertEqual(record["request_id"], "test-id")
            self.assertTrue(record["stream_done"])
            self.assertEqual(inspect_response(record, cfg)["status"], "completed")

    def test_http_error_classification_no_sdk_retry(self):
        cfg = config()
        with patch("sl.live_transport.os.environ.get", return_value="UNIT_TEST_FAKE_KEY"), patch("sl.live_transport.request.build_opener") as builder:
            builder.return_value.open.side_effect = HTTPError(ENDPOINT, 401, "denied", {}, None)
            result = OpenRouterTransport(cfg, go(cfg)).send(wire_request([], cfg))
            self.assertEqual(builder.return_value.open.call_count, 1)
            self.assertTrue(inspect_response(result, cfg)["fatal"])
            self.assertFalse(result["retryable"])
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://example.invalid"))

    def test_route_has_no_fallback_and_no_reasoning_text(self):
        payload = wire_request([], config())
        self.assertEqual(payload["provider"]["only"], ["alibaba"])
        self.assertFalse(payload["provider"]["allow_fallbacks"])
        self.assertTrue(payload["provider"]["require_parameters"])
        self.assertTrue(payload["stream"])
        self.assertEqual(payload["stream_options"], {"include_usage": True})
        self.assertTrue(payload["reasoning"]["exclude"])
        self.assertEqual(payload["reasoning"], {"enabled": True, "exclude": True})
        self.assertEqual(payload["top_p"], 0.95)
        envelope = response()["visible_response"]
        self.assertNotIn("never log this", str(envelope))
        self.assertEqual(envelope["choices"][0]["message"]["content"], "visible")

    def test_provider_usage_and_cost(self):
        result = inspect_response(response(), config())
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["usage"]["output_tokens"], 100)
        self.assertEqual(result["usage"]["reasoning_tokens"], 30)
        self.assertEqual(result["charge_for_ledger"], Decimal("0.000468"))

    def test_truncation_not_a_retry(self):
        result = inspect_response(response("", finish="length"), config())
        self.assertEqual(result["status"], "model_truncated")
        self.assertFalse(result["retryable"])
        self.assertFalse(result["fatal"])

    def test_route_mismatch_stops(self):
        result = inspect_response(response(provider="Another"), config())
        self.assertTrue(result["fatal"])
        self.assertEqual(result["status"], "provider_contract_error")

    def test_unknown_billing_not_zero(self):
        result = inspect_response(response(cost=None), config())
        self.assertEqual(result["status"], "completed")
        self.assertIsNone(result["charge_for_ledger"])

    def test_corrupt_usage_fails_closed(self):
        for key, value in (("cost", -1), ("prompt_tokens", True), ("completion_tokens", -1)):
            record = response()
            record["visible_response"]["usage"][key] = value
            self.assertTrue(inspect_response(record, config())["fatal"])

    def test_retry_eligibility_is_reconstructed(self):
        for record in (response(), response(finish="length")):
            record["retryable"] = True
            with self.assertRaisesRegex(ValueError, "retry eligibility"):
                inspect_response(record, config())
        record = response()
        record.update(http_status=401, technical_error="http_401", retryable=True)
        with self.assertRaisesRegex(ValueError, "retry eligibility"):
            inspect_response(record, config())

    def test_provider_id_role_and_total_usage(self):
        record = response(generation_id="")
        self.assertTrue(inspect_response(record, config())["fatal"])
        record = response()
        record["visible_response"]["usage"]["total_tokens"] = 100
        self.assertTrue(inspect_response(record, config())["fatal"])
        record = response()
        record["visible_response"]["choices"][0]["message"]["role"] = "user"
        self.assertTrue(inspect_response(record, config())["fatal"])


class WalletTests(unittest.TestCase):
    def test_global_retry_ceiling_survives_stage_and_restart(self):
        cfg = config()
        cfg["max_technical_retries"] = 1
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wallet"
            ledger = Ledger(path, cfg, create=True)
            ledger.start_stage("pilot", "pilot-manifest")
            ledger.reserve("pilot/first", "pilot", retry=True)
            ledger.settle("pilot/first", None, "transport_error")
            ledger = Ledger(path, cfg)
            ledger.start_stage("main", "main-manifest")
            with self.assertRaisesRegex(BudgetStop, "global technical retry"):
                ledger.reserve("main/second", "main", retry=True)
            self.assertEqual(audit_ledger(ledger.snapshot(), cfg)["retries"], 1)

    def test_full_campaign_upper_bound_is_not_spending_authority(self):
        self.assertEqual(reservation(config()), Decimal("0.61341696"))
        self.assertEqual(reservation(config()) * 788, Decimal("483.37256448"))
        self.assertGreater(reservation(config()) * 788, Decimal("30"))

    def test_persistent_unknown_reservation_and_no_overdraft(self):
        cfg = config()
        cfg["budget_usd"] = str(reservation(cfg) * 2)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wallet.jsonl"
            ledger = Ledger(path, cfg, create=True)
            ledger.start_stage("pilot", "manifest")
            ledger.reserve("a", "pilot")
            ledger.settle("a", None, "transport_error")
            ledger = Ledger(path, cfg)
            ledger.reserve("b", "pilot", retry=True)
            ledger.settle("b", None, "transport_error")
            with self.assertRaises(BudgetStop):
                ledger.reserve("c", "pilot")
            self.assertEqual(audit_ledger(ledger.snapshot(), cfg)["charged_or_reserved"], reservation(cfg) * 2)

    def test_actual_charge_releases_unused_reserve(self):
        cfg = config()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "wallet", cfg, create=True)
            ledger.start_stage("pilot", "manifest")
            ledger.reserve("a", "pilot")
            ledger.settle("a", "0.001", "completed")
            self.assertEqual(audit_ledger(ledger.snapshot(), cfg)["charged_or_reserved"], Decimal("0.001"))

    def test_inflight_crash_blocks_second_dispatch(self):
        cfg = config()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wallet"
            ledger = Ledger(path, cfg, create=True)
            ledger.start_stage("pilot", "manifest")
            ledger.reserve("a", "pilot")
            with self.assertRaises(BudgetStop):
                Ledger(path, cfg).reserve("b", "pilot")
            with self.assertRaises(BudgetStop):
                Ledger(path, cfg).start_stage("main", "other")

    def test_stage_cannot_be_restarted(self):
        cfg = config()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "wallet", cfg, create=True)
            ledger.start_stage("pilot", "manifest")
            with self.assertRaises(BudgetStop):
                ledger.start_stage("pilot", "manifest")

    def test_cost_ceiling_violation_stops_future_requests(self):
        cfg = config()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "wallet", cfg, create=True)
            ledger.start_stage("pilot", "manifest")
            ledger.reserve("a", "pilot")
            with self.assertRaises(BudgetStop):
                ledger.settle("a", "1", "completed")
            with self.assertRaises(BudgetStop):
                ledger.reserve("b", "pilot")


class StreamTests(unittest.TestCase):
    def test_fragmented_utf8_comments_and_usage_only_final(self):
        frames = stream_frames()
        frames[1]["choices"][0]["delta"]["content"] = "答"
        frames[2]["choices"][0]["delta"]["content"] = "案"
        raw = stream_bytes(frames)
        class Fragmented(io.RawIOBase):
            def __init__(self):
                self.position = 0
            def readable(self):
                return True
            def readinto(self, buffer):
                part = raw[self.position:self.position + min(3, len(buffer))]
                buffer[:len(part)] = part
                self.position += len(part)
                return len(part)
        record = stream_record()
        with patch("sl.live_transport.time.perf_counter", return_value=0):
            read_sse(io.BufferedReader(Fragmented()), record, config(), 1, lambda seconds: None)
        self.assertEqual(record["visible_response"]["choices"][0]["message"]["content"], "答案")
        self.assertEqual(record["visible_response"]["usage"]["total_tokens"], 1100)
        self.assertNotIn("HIDDEN_FIXTURE_REASONING", str(record))
        self.assertEqual(record["response_bytes"], len(raw))

    def test_missing_done_finish_or_usage_is_not_complete(self):
        variants = [(stream_frames(), False), (stream_frames()[:-1], True)]
        no_finish = stream_frames()
        no_finish[2]["choices"][0]["finish_reason"] = None
        variants.append((no_finish, True))
        for frames, done in variants:
            with self.subTest(done=done, frames=len(frames)):
                record = stream_record()
                with patch("sl.live_transport.time.perf_counter", return_value=0), self.assertRaises(ValueError):
                    read_sse(io.BytesIO(stream_bytes(frames, done)), record, config(), 1, lambda seconds: None)
                self.assertIsNone(record["visible_response"])

    def test_midstream_error_is_not_an_answer(self):
        frames = stream_frames()[:2] + [{"error": {"code": 500, "message": "DO_NOT_RETAIN_SERVER_TEXT"}}]
        record = stream_record()
        with patch("sl.live_transport.time.perf_counter", return_value=0), self.assertRaises(ValueError):
            read_sse(io.BytesIO(stream_bytes(frames)), record, config(), 1, lambda seconds: None)
        self.assertNotIn("DO_NOT_RETAIN_SERVER_TEXT", str(record))

    def test_changed_identity_is_rejected(self):
        for field in ("id", "model", "provider"):
            events = [visible_stream_event(frame) for frame in stream_frames()]
            events[1][field] = "changed"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "identity"):
                assemble_stream(events, True)

    def test_byte_and_wall_time_bounds(self):
        cfg = config()
        cfg["max_response_utf8_bytes"] = 30
        with patch("sl.live_transport.time.perf_counter", return_value=0), self.assertRaisesRegex(ValueError, "byte ceiling"):
            read_sse(io.BytesIO(stream_bytes()), stream_record(), cfg, 1, lambda seconds: None)
        with patch("sl.live_transport.time.perf_counter", return_value=2), self.assertRaises(TimeoutError):
            read_sse(io.BytesIO(stream_bytes()), stream_record(), config(), 1, lambda seconds: None)

    def test_partial_timeout_keeps_transport_unknown(self):
        cfg = config()
        class HTTPResponse:
            status = 200
            headers = {"content-type": "text/event-stream"}
            fp = SimpleNamespace(raw=SimpleNamespace(_sock=SimpleNamespace(settimeout=lambda seconds: None)))
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def readline(self, limit): raise TimeoutError("fixture")
        with patch("sl.live_transport.os.environ.get", return_value="UNIT_TEST_FAKE_KEY"), patch("sl.live_transport.request.build_opener") as builder:
            builder.return_value.open.return_value = HTTPResponse()
            record = OpenRouterTransport(cfg, go(cfg)).send(wire_request([], cfg))
        self.assertEqual(record["technical_error"], "transport_failure")
        self.assertFalse(record["stream_done"])
        self.assertIsNone(inspect_response(record, cfg)["charge_for_ledger"])


class LivePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.run_data = fixture_run()

    def test_matrix_audit_and_nonempirical_label(self):
        self.assertEqual(len(self.run_data["calls"]), 108)
        self.assertTrue(audit_live(self.manifest, self.run_data)["passed"])
        gate = live_gate(self.manifest, self.run_data)
        self.assertTrue(gate["interface_thresholds_pass"])
        self.assertFalse(gate["passed"])
        self.assertEqual(gate["valid_role_responses"], 108)

    def test_fresh_values_and_clean_first(self):
        original = {s.facts for s in generate("dev") + generate("validation", 2802)}
        pilot = fresh_cases("pilot", 1)
        main = fresh_cases("main", 2)
        self.assertFalse(original & {s.facts for s in pilot + main})
        self.assertFalse({s.facts for s in pilot} & {s.facts for s in main})
        self.assertTrue(all(item["scenario_id"].endswith("-clean") for item in self.manifest["schedule"][:4]))

    def test_inspected_live_fixtures_cannot_be_acquired_as_fresh(self):
        with self.assertRaisesRegex(ValueError, "inspected live-interface fixture"):
            live_manifest(config(), "pilot", 2026110801)
        with self.assertRaisesRegex(ValueError, "inspected live-interface fixture"):
            check_fixture_separation(fresh_cases("main", 2))

    def test_main_requires_real_pilot(self):
        with self.assertRaises(ValueError):
            live_manifest(config(), "main", 2)
        fake = {"manifest": self.manifest, "run_hash": digest(self.run_data), "gate": {"passed": True}}
        with self.assertRaisesRegex(ValueError, "fixture"):
            live_manifest(config(), "main", 2, pilot=fake)

    def test_manifest_and_order_tampering(self):
        changed = deepcopy(self.manifest)
        changed["schedule"].reverse()
        changed["manifest_hash"] = digest({k: v for k, v in changed.items() if k != "manifest_hash"})
        with self.assertRaisesRegex(ValueError, "order"):
            validate_live_manifest(changed)

    def test_rehashed_retry_budget_tampering(self):
        changed = deepcopy(self.manifest)
        changed["retry_budget"] = 100
        changed["manifest_hash"] = digest({k: v for k, v in changed.items() if k != "manifest_hash"})
        with self.assertRaisesRegex(ValueError, "frozen limits"):
            validate_live_manifest(changed)

    def test_main_rechecks_actual_pilot_binding(self):
        # Unit-test the binding predicate with a mocked audit result. This is
        # not a recorded HTTP run and cannot pass the real acquisition gate.
        cfg = config()
        pilot_manifest = {"manifest_hash": "pilot-hash", "acquisition_mode": "official_https",
                          "config": cfg, "code_hashes": code_hashes()}
        pilot_run = {"ledger": [{"fixture": "prefix"}], "observations": "UNIT_TEST_ONLY"}
        gate = {"passed": True}
        main = {"phase": "main", "config": cfg, "code_hashes": code_hashes(),
                "pilot_binding": {"manifest_hash": "pilot-hash", "run_hash": digest(pilot_run), "gate": gate}}
        with patch("sl.live_run.live_gate", return_value=gate):
            verify_pilot_binding(main, pilot_manifest, pilot_run, pilot_run["ledger"])
            changed = deepcopy(pilot_run)
            changed["observations"] = "changed"
            with self.assertRaisesRegex(ValueError, "actual pilot"):
                verify_pilot_binding(main, pilot_manifest, changed, pilot_run["ledger"])
            with self.assertRaisesRegex(ValueError, "actual pilot"):
                verify_pilot_binding(main, pilot_manifest, pilot_run, [])
        with patch("sl.live_run.live_gate", return_value={"passed": False}):
            with self.assertRaisesRegex(ValueError, "actual pilot"):
                verify_pilot_binding(main, pilot_manifest, pilot_run, pilot_run["ledger"])

    def test_response_tampering(self):
        changed = deepcopy(self.run_data)
        changed["calls"][0]["cost_usd"] = 0
        with self.assertRaisesRegex(ValueError, "normalization"):
            audit_live(self.manifest, changed)

    def test_duplicate_provider_id_rejected(self):
        changed = deepcopy(self.run_data)
        changed["calls"][1]["acquisition"]["visible_response"]["id"] = changed["calls"][0]["acquisition"]["visible_response"]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate provider"):
            audit_live(self.manifest, changed)

    def test_ledger_tampering(self):
        changed = deepcopy(self.run_data)
        changed["ledger"][2]["reserved_usd"] = "0"
        with self.assertRaisesRegex(ValueError, "hash chain"):
            audit_live(self.manifest, changed)

    def test_content_hash_tampering(self):
        changed = deepcopy(self.run_data)
        changed["rows"][0]["content_hash"] = "forged"
        with self.assertRaisesRegex(ValueError, "content/request"):
            audit_live(self.manifest, changed)

    def test_transport_missingness_and_outage_circuit(self):
        manifest, run = fixture_run(fail=True)
        self.assertTrue(audit_live(manifest, run)["passed"])
        self.assertEqual(run["retries_used"], 3)
        self.assertEqual(run["requests_attempted"], 6)
        self.assertEqual(run["stop_reason"], "three_consecutive_failed_logical_transports")
        self.assertTrue(all(row["score"] is None for row in run["rows"]))
        self.assertFalse(live_gate(manifest, run)["passed"])

    def test_model_truncation_does_not_trip_outage_circuit(self):
        cfg = config()
        manifest = live_manifest(cfg, "pilot", 2026110801, fixture=True)
        class Truncated(FixtureTransport):
            def send(self, payload):
                self.responses += 1
                return response("", finish="length", generation_id=f"truncated-{self.responses}")
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "wallet", cfg, create=True)
            run = LiveRunner(manifest, Truncated(cfg), ledger, go(cfg)).run()
        self.assertIsNone(run["stop_reason"])
        self.assertEqual(run["retries_used"], 0)
        self.assertTrue(audit_live(manifest, run)["passed"])

    def test_analysis_keeps_fixture_nonempirical(self):
        result = analyze(self.manifest, self.run_data)
        self.assertEqual(result["cost"]["external_api_requests"], 0)
        self.assertFalse(result["pilot_gate"]["passed"])
        self.assertEqual(len(result["clean_originals"]), 4)


if __name__ == "__main__":
    unittest.main()