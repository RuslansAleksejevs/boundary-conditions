"""Transport fixtures only. These tests never contact a model or load a credential."""

import copy
import contextlib
import io
import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from wgp.certificates import solve
from wgp.dataset import (audit_dataset, exclusion_sets, make_dataset, make_exclusions,
                         signature, skeleton)
from wgp.live import (FIXTURE_KIND, actual_pilot_separation, audit_campaign, audit_live, freeze_live, known_transport_fixture_datasets,
                      load_live, prepare_live, revised_pilot_manifest, run_live_stage, scheduled_ids, validate_go)
from wgp.live_budget import BudgetLedger, BudgetStop, ledger_state, money
from wgp.live_http import (budget_configuration_hash, interpret_receipt, payload_for,
                           upper_cost, validate_configuration, visible_response)
from wgp.logic import SchemaError, canonical, digest, parse_rendered_contract, strict_json
from wgp.pipeline import audit_run, timestamp
from wgp.prompts import translation_request
from wgp.records import read_json, write_new


def fixture_config():
    # Illustrative parser/budget-test values, NOT a verified tariff or approval.
    return {"version": 1, "model": "openai/gpt-oss-120b", "provider_slug": "together",
            "provider_response_name": "Together", "temperature": 0, "top_p": 1,
            "reasoning_effort": "low", "max_tokens": 4096, "context_token_bound": 131072,
            "output_reservation_tokens": 8192,
            "max_request_bytes": 24000, "timeout_seconds": 60,
            "input_usd_per_million": "0.15", "output_usd_per_million": "0.60",
            "request_usd": "0", "quota_usd": "20",
            "data_collection": "deny", "version_pin_status": "fixture-only; no immutable revision claim",
            "price_source": "https://example.invalid/fixture-not-a-tariff", "price_as_of": "fixture-only"}


def fixture_go(manifest):
    return {"version": 1, "decision": "GO", "study": "wrong-goal-proof",
            "configuration_hash": manifest["configuration_hash"],
            "manifest_hash": digest(manifest), "allowed_stages": ["pilot-v1", "main"],
            "code_hashes_hash": digest(manifest["code_hashes"]), "approved_at": timestamp(),
            "authorization_reference": "TRANSPORT_FIXTURE_ONLY_NOT_REAL_AUTHORIZATION", "quota_usd": "20"}


class FixtureHTTP:
    kind = "fixture_http_no_network"

    def __init__(self, error=None):
        self.count, self.error = 0, error

    def send(self, payload):
        self.count += 1
        now = timestamp()
        result = {"started_at": now, "finished_at": now, "latency_seconds": 0.0,
                  "http_status": 200, "headers": {}, "transport_error": None,
                  "retryable_transport": False}
        if self.error == "timeout":
            return {**result, "http_status": None, "response": None,
                    "transport_error": "timeout", "retryable_transport": True}
        data = strict_json(payload["messages"][1]["content"])
        original = parse_rendered_contract(data["original_task"])
        if payload["messages"][0]["content"].startswith("Translate"):
            answer = original
        else:
            certificate = solve(original)
            answer = {"verdict": certificate["verdict"], "witness": certificate.get("witness")}
        response = {"id": "fixture-acquisition-" + str(self.count), "model": payload["model"],
                    "provider": "Together", "choices": [{"finish_reason": "stop",
                    "message": {"role": "assistant", "content": canonical(answer)}}],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300,
                              "completion_tokens_details": {"reasoning_tokens": 70},
                              "prompt_tokens_details": {"cached_tokens": 0}, "cost": 0.000135}}
        if self.error == "length":
            response["choices"][0]["finish_reason"] = "length"
        if self.error == "provider":
            response["provider"] = "not-approved"
        if self.error == "duplicate":
            response["id"] = "fixture-duplicate"
        if self.error == "schema":
            response["choices"][0]["message"]["content"] = "not JSON"
        if self.error == "401":
            return {**result, "http_status": 401, "response": {"error": {"code": 401}}}
        return {**result, "response": response}


class ExclusionTests(unittest.TestCase):
    def test_old_engineering_dataset_digest_unchanged(self):
        self.assertEqual(digest(make_dataset(6006)), "2d050c8704bf65e95c16424b97ba3001c900b522d2adc5c1304a736b25c2a46e")

    def test_cross_bundle_functions_and_original_shapes_excluded(self):
        excluded = make_exclusions([make_dataset(6006), make_dataset(6007)])
        semantic, shapes = exclusion_sets(excluded)
        fresh = make_dataset(2026110806, exclusions=excluded)
        self.assertTrue(audit_dataset(fresh)["valid"])
        for cases in fresh["splits"].values():
            for case in cases:
                self.assertNotIn(skeleton(case["original"]), shapes)
                for name in ("original", "candidate"):
                    if case[name] is not None:
                        self.assertNotIn(signature(case[name]), semantic)

    def test_tampered_exclusion_hash_rejected(self):
        excluded = make_exclusions([make_dataset(6006)])
        excluded["semantic"].pop()
        with self.assertRaises(SchemaError):
            make_dataset(2026110806, exclusions=excluded)

    def test_both_transport_fixture_recipes_are_exact_and_different(self):
        first, second = known_transport_fixture_datasets()
        self.assertNotEqual(digest(first), digest(second))
        self.assertEqual([len(d["exclusions"]["sources"]) for d in (first, second)], [2, 12])

    def test_exclusion_source_schema_duplicate_and_nonobject_dataset(self):
        excluded = make_exclusions([make_dataset(6006)])
        for field, value in (("sources", excluded["sources"] * 2), ("semantic", {}), ("original_skeletons", [[]])):
            bad = {**excluded, field: value}
            bad["hash"] = digest({k: v for k, v in bad.items() if k != "hash"}, "wgp-exclusions-v1")
            with self.subTest(field=field), self.assertRaises(SchemaError):
                exclusion_sets(bad)
        with self.assertRaises(SchemaError):
            audit_dataset([])


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "budget.jsonl"

    def test_unknown_charge_survives_restart_and_blocks_overspend(self):
        with BudgetLedger(self.path, "config") as ledger:
            aid = ledger.reserve("r1", "pilot-v1", "request", "19")
            ledger.settle(aid, None, False, {"status": "timeout"})
        with BudgetLedger(self.path, "config") as ledger:
            self.assertEqual(money(ledger.state()["committed_usd"]), money("19"))
            with self.assertRaises(BudgetStop):
                ledger.reserve("r2", "pilot-v1", "request2", "2")

    def test_known_charge_releases_only_unused_reservation(self):
        with BudgetLedger(self.path, "config") as ledger:
            aid = ledger.reserve("r1", "pilot-v1", "request", "19")
            ledger.settle(aid, "0.25", False, {})
            ledger.reserve("r2", "pilot-v1", "request2", "19")
            self.assertEqual(money(ledger.state()["committed_usd"]), money("19.25"))

    def test_reserve_without_settlement_stays_fully_committed(self):
        with BudgetLedger(self.path, "config") as ledger:
            ledger.reserve("r1", "pilot-v1", "request", "20")
        with BudgetLedger(self.path, "config") as ledger:
            with self.assertRaises(BudgetStop):
                ledger.reserve("r2", "pilot-v1", "request2", "0.01")

    def test_only_one_identical_technical_retry(self):
        with BudgetLedger(self.path, "config") as ledger:
            first = ledger.reserve("r1", "pilot-v1", "request", "0.01")
            ledger.settle(first, None, True, {})
            with self.assertRaises(BudgetStop):
                ledger.reserve("r1", "pilot-v1", "changed", "0.01", retry_of=first)
            second = ledger.reserve("r1", "pilot-v1", "request", "0.01", retry_of=first)
            ledger.settle(second, None, True, {})
            with self.assertRaises(BudgetStop):
                ledger.reserve("r1", "pilot-v1", "request", "0.01", retry_of=second)

    def test_no_semantic_retry_or_duplicate_logical_call(self):
        with BudgetLedger(self.path, "config") as ledger:
            first = ledger.reserve("r1", "pilot-v1", "request", "0.01")
            ledger.settle(first, "0.001", False, {})
            with self.assertRaises(BudgetStop):
                ledger.reserve("r1", "pilot-v1", "request", "0.01", retry_of=first)
            with self.assertRaises(BudgetStop):
                ledger.reserve("r1", "pilot-v1", "request", "0.01")

    def test_fifteen_total_retries_not_per_stage(self):
        with BudgetLedger(self.path, "config") as ledger:
            for i in range(15):
                first = ledger.reserve(str(i), "pilot-v1", str(i), "0.001")
                ledger.settle(first, None, True, {})
                second = ledger.reserve(str(i), "pilot-v1", str(i), "0.001", retry_of=first)
                ledger.settle(second, None, False, {})
            first = ledger.reserve("next", "main", "next", "0.001")
            ledger.settle(first, None, True, {})
            with self.assertRaises(BudgetStop):
                ledger.reserve("next", "main", "next", "0.001", retry_of=first)

    def test_pilot_logical_cap(self):
        with BudgetLedger(self.path, "config") as ledger:
            for i in range(52):
                ledger.reserve(str(i), "pilot-v1", str(i), "0.001")
            with self.assertRaises(BudgetStop):
                ledger.reserve("extra", "pilot-v1", "extra", "0.001")

    def test_known_pricing_overrun_halts_further_calls(self):
        with BudgetLedger(self.path, "config") as ledger:
            aid = ledger.reserve("r1", "pilot-v1", "request", "0.01")
            ledger.settle(aid, "0.02", False, {})
            self.assertTrue(ledger.state()["pricing_overrun"])
            with self.assertRaises(BudgetStop):
                ledger.reserve("r2", "pilot-v1", "request2", "0.01")

    def test_lock_hash_and_torn_journal_fail_closed(self):
        with BudgetLedger(self.path, "config") as ledger:
            ledger.reserve("r1", "pilot-v1", "request", "0.01")
            with self.assertRaises(BlockingIOError):
                with BudgetLedger(self.path, "config"):
                    pass
        with self.assertRaises(SchemaError):
            with BudgetLedger(self.path, "different-config"):
                pass
        self.path.write_text(self.path.read_text()[:-1])
        with self.assertRaises(SchemaError):
            with BudgetLedger(self.path, "config"):
                pass

    def test_money_types(self):
        self.assertEqual(money(Decimal("0.01")), Decimal("0.01"))
        for value in (True, "NaN", "Infinity", "-1", None):
            with self.subTest(value=value), self.assertRaises(SchemaError):
                money(value)

    def test_retry_count_survives_close_and_new_stage(self):
        with BudgetLedger(self.path, "config") as ledger:
            first = ledger.reserve("r1", "pilot-v1", "request", money("0.01"))
            ledger.settle(first, None, True, {})
            second = ledger.reserve("r1", "pilot-v1", "request", money("0.01"), retry_of=first)
            ledger.settle(second, None, False, {})
        with BudgetLedger(self.path, "config") as ledger:
            self.assertEqual(ledger.state()["retries"], 1)
            ledger.reserve("r1", "main", "request", money("0.01"))
            self.assertEqual(ledger.state()["retries"], 1)


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = translation_request(make_dataset()["splits"]["dev"][0])

    def test_no_fallback_no_tools_no_hidden_reasoning_and_explicit_caps(self):
        body = payload_for(self.request, fixture_config())
        self.assertEqual(body["provider"]["only"], ["together"])
        self.assertFalse(body["provider"]["allow_fallbacks"])
        self.assertTrue(body["provider"]["require_parameters"])
        self.assertTrue(body["reasoning"]["exclude"])
        self.assertNotIn("tools", body)
        self.assertEqual(body["plugins"], [])
        self.assertLess(379 * upper_cost(fixture_config()), money("20"))

    def test_unapproved_model_oversized_request_and_unaffordable_caps_rejected(self):
        for change in ({"model": "other"}, {"max_tokens": 131072}, {"input_usd_per_million": "1000"}, {"quota_usd": "50"}):
            with self.subTest(change=change), self.assertRaises(SchemaError):
                validate_configuration({**fixture_config(), **change})
        with self.assertRaises(SchemaError):
            payload_for(self.request, {**fixture_config(), "max_request_bytes": 10})

    def test_wrong_provider_usage_and_false_retry_flag_rejected(self):
        body = payload_for(self.request, fixture_config())
        receipt = FixtureHTTP("provider").send(body)
        self.assertEqual(interpret_receipt(receipt, fixture_config())["status"], "integrity_error")
        receipt = FixtureHTTP().send(body)
        receipt["response"]["usage"]["completion_tokens"] = 10_000
        self.assertEqual(interpret_receipt(receipt, fixture_config())["status"], "integrity_error")
        receipt = FixtureHTTP().send(body)
        receipt["retryable_transport"] = True
        with self.assertRaises(SchemaError):
            interpret_receipt(receipt, fixture_config())

    def test_length_is_an_outcome_never_a_retry(self):
        receipt = FixtureHTTP("length").send(payload_for(self.request, fixture_config()))
        result = interpret_receipt(receipt, fixture_config())
        self.assertEqual(result["status"], "truncated")
        self.assertFalse(result["retryable"])

    def test_explicit_output_margin_does_not_change_requested_cap(self):
        config = fixture_config()
        body = payload_for(self.request, config)
        self.assertEqual(body["max_tokens"], 4096)
        receipt = FixtureHTTP().send(body)
        usage = receipt["response"]["usage"]
        usage.update(completion_tokens=4098, total_tokens=4198)
        self.assertEqual(interpret_receipt(receipt, config)["status"], "response")
        usage.update(completion_tokens=8193, total_tokens=8293)
        self.assertEqual(interpret_receipt(receipt, config)["status"], "integrity_error")
        with self.assertRaises(SchemaError):
            validate_configuration({**config, "output_reservation_tokens": 4095})

    def test_missing_cost_is_unknown_and_invalid_total_or_role_is_fatal(self):
        receipt = FixtureHTTP().send(payload_for(self.request, fixture_config()))
        receipt["response"]["usage"].pop("cost")
        self.assertIsNone(interpret_receipt(receipt, fixture_config())["usage"]["cost_usd"])
        receipt["response"]["usage"]["total_tokens"] = 300.0
        self.assertTrue(interpret_receipt(receipt, fixture_config())["fatal"])
        receipt["response"]["usage"]["total_tokens"] = 300
        receipt["response"]["choices"][0]["message"]["role"] = "user"
        self.assertTrue(interpret_receipt(receipt, fixture_config())["fatal"])

    def test_missing_provider_empty_id_and_unexpected_function_are_fatal(self):
        for change in ("provider", "id", "function"):
            receipt = FixtureHTTP().send(payload_for(self.request, fixture_config()))
            if change == "provider":
                receipt["response"].pop("provider")
            elif change == "id":
                receipt["response"]["id"] = "   "
            else:
                receipt["response"]["choices"][0]["message"]["function_call"] = {"name": "unexpected"}
            with self.subTest(change=change):
                self.assertTrue(interpret_receipt(receipt, fixture_config())["fatal"])

    def test_explicit_data_policy_and_no_redirect(self):
        from wgp.live_http import NoRedirect
        self.assertEqual(payload_for(self.request, fixture_config())["provider"]["data_collection"], "deny")
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, None, None, "https://example.invalid"))
        with self.assertRaises(SchemaError):
            validate_configuration({**fixture_config(), "data_collection": None})

    def test_hidden_reasoning_text_is_not_kept(self):
        normalized = visible_response({"choices": [{"message": {"content": "visible", "reasoning": "hidden", "reasoning_details": []}}],
                                       "usage": {"reasoning_tokens": 7}})
        self.assertEqual(normalized["choices"][0]["message"], {"content": "visible"})
        self.assertEqual(normalized["usage"]["reasoning_tokens"], 7)


class LiveWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "campaign"
        self.manifest = prepare_live(self.path, fixture_config(), 2026110806)
        self.dataset, _ = load_live(self.path)
        self.go = fixture_go(self.manifest)

    def test_all_inspected_seed_bundles_excluded_and_first_calls_clean(self):
        self.assertEqual(len(self.dataset["exclusions"]["sources"]), 12)
        by_id = {c["id"]: c for c in self.dataset["splits"]["dev"]}
        first = self.manifest["orders"]["dev"]["cases"][:2]
        self.assertEqual([by_id[i]["family"] for i in first], ["SAFE", "UNSAFE"])
        self.assertTrue(all(by_id[i]["group"] == "natural" for i in first))

    def test_actual_pilot_translation_collision_blocks_future_holdout(self):
        # Deliberately constructed metadata fixture; not an acquired pilot.
        clean = {"outcomes": [{"candidate": c["original"]} for c in self.dataset["splits"]["dev"]]}
        self.assertTrue(actual_pilot_separation(self.dataset, clean)["valid"])
        collision = {"outcomes": [{"candidate": self.dataset["splits"]["holdout"][0]["original"]}]}
        self.assertFalse(actual_pilot_separation(self.dataset, collision)["valid"])
        self.assertEqual(actual_pilot_separation(self.dataset, collision)["overlapping_functions"], 1)

    def test_clean_second_pilot_does_not_erase_first_pilot_collision(self):
        first = {"outcomes": [{"candidate": self.dataset["splits"]["holdout"][0]["original"]}]}
        second = {"outcomes": [{"candidate": self.dataset["splits"]["dev"][0]["original"]}]}
        self.assertTrue(actual_pilot_separation(self.dataset, second)["valid"])
        combined = actual_pilot_separation(self.dataset, second, previous_pilots=[first])
        self.assertFalse(combined["valid"])
        self.assertEqual(combined["preserved_pilots_checked"], 2)

    def test_no_go_and_wrong_hash_stop_before_transport(self):
        transport = FixtureHTTP()
        with self.assertRaises(SchemaError):
            run_live_stage(self.path, "pilot-v1", {**self.go, "decision": "PENDING"}, transport=transport)
        self.assertEqual(transport.count, 0)
        with self.assertRaises(SchemaError):
            validate_go({**self.go, "code_hashes_hash": "wrong"}, self.manifest)
        with self.assertRaises(SchemaError):
            validate_go({**self.go, "manifest_hash": "wrong"}, self.manifest)
        with self.assertRaises(SchemaError):
            validate_go(self.go, self.manifest, "pilot-v2")

    def test_fixture_receipts_audited_but_cannot_qualify_as_real_model_pilot(self):
        run = run_live_stage(self.path, "pilot-v1", self.go, transport=FixtureHTTP())
        self.assertEqual(run["adapter"]["kind"], FIXTURE_KIND)
        self.assertEqual(run["new_model_calls"], 0)
        result = audit_live(self.dataset, self.manifest, run, allow_fixture=True)
        self.assertEqual(result["physical_attempts"], 52)
        self.assertTrue(all(o["correct"] for o in run["outcomes"]))
        with self.assertRaises(SchemaError):
            audit_live(self.dataset, self.manifest, run)
        with self.assertRaises(SchemaError):
            audit_run(self.dataset, run)
        with self.assertRaises(SchemaError):
            freeze_live(self.path)
        self.assertEqual(audit_campaign(self.path, allow_fixture=True)["new_model_calls"], 0)
        with self.assertRaises(SchemaError):
            audit_campaign(self.path)
        from wgp.live_evidence import export_live_evidence
        with self.assertRaises(SchemaError):
            export_live_evidence(self.dataset, self.manifest, run)

    def test_timeout_retains_charges_and_stops_after_three_logical_failures(self):
        transport = FixtureHTTP("timeout")
        run = run_live_stage(self.path, "pilot-v1", self.go, transport=transport)
        result = audit_live(self.dataset, self.manifest, run, allow_fixture=True)
        self.assertEqual(transport.count, 6)
        self.assertEqual(result["ledger"]["unknown_charges"], 6)
        self.assertEqual(money(result["ledger"]["committed_usd"]), 6 * upper_cost(fixture_config()))
        self.assertIsNotNone(run["halt_reason"])

    def test_audit_rejects_receipt_order_prompt_cost_or_deleted_attempt(self):
        run = run_live_stage(self.path, "pilot-v1", self.go, transport=FixtureHTTP())
        for mutation in ("order", "payload", "cost", "missing"):
            changed = copy.deepcopy(run)
            if mutation == "order":
                changed["calls"][0], changed["calls"][1] = changed["calls"][1], changed["calls"][0]
            elif mutation == "payload":
                changed["receipts"][0]["payload"]["messages"][0]["content"] = "changed"
            elif mutation == "cost":
                changed["receipts"][0]["response"]["usage"]["cost"] = 0
            else:
                changed["receipts"].pop()
            with self.subTest(mutation=mutation), self.assertRaises(SchemaError):
                audit_live(self.dataset, self.manifest, changed, allow_fixture=True)

    def test_one_identical_timeout_retry_not_a_new_logical_sample(self):
        class OnceTimeout(FixtureHTTP):
            def send(self, payload):
                self.error = "timeout" if self.count == 0 else None
                return super().send(payload)
        transport = OnceTimeout()
        run = run_live_stage(self.path, "pilot-v1", self.go, transport=transport)
        audit = audit_live(self.dataset, self.manifest, run, allow_fixture=True)
        self.assertEqual((audit["physical_attempts"], audit["ledger"]["retries"]), (53, 1))
        self.assertEqual(run["receipts"][0]["payload"], run["receipts"][1]["payload"])
        self.assertTrue(all(o["correct"] for o in run["outcomes"]))

    def test_401_stops_without_retry_and_unknown_charge_is_reserved(self):
        transport = FixtureHTTP("401")
        run = run_live_stage(self.path, "pilot-v1", self.go, transport=transport)
        audit = audit_live(self.dataset, self.manifest, run, allow_fixture=True)
        self.assertEqual(transport.count, 1)
        self.assertEqual(audit["ledger"]["unknown_charges"], 1)
        self.assertTrue(run["halt_reason"])

    def test_model_schema_errors_are_not_retried_and_no_gold_translation_is_inserted(self):
        transport = FixtureHTTP("schema")
        run = run_live_stage(self.path, "pilot-v1", self.go, transport=transport)
        audit = audit_live(self.dataset, self.manifest, run, allow_fixture=True)
        self.assertEqual((transport.count, audit["ledger"]["retries"]), (44, 0))
        natural = [o for o in run["outcomes"] if o["group"] == "natural"]
        self.assertTrue(all(o["candidate"] is None and o["status"] == "blocked_translation" for o in natural))

    def test_duplicate_acquisition_stops_immediately_and_remains_in_private_journal(self):
        transport = FixtureHTTP("duplicate")
        with self.assertRaises(SchemaError):
            run_live_stage(self.path, "pilot-v1", self.go, transport=transport)
        self.assertEqual(transport.count, 2)
        self.assertIn("fixture-duplicate", (self.path / "pilot-v1" / "events.jsonl").read_text())
        with self.assertRaises(FileNotFoundError):
            audit_campaign(self.path, allow_fixture=True)

    def test_forged_freeze_cannot_turn_fixture_pilot_into_empirical_main(self):
        run = run_live_stage(self.path, "pilot-v1", self.go, transport=FixtureHTTP())
        write_new(self.path / "freeze.json", {
            "manifest_name": "manifest.json", "manifest_hash": digest(self.manifest),
            "code_hashes": self.manifest["code_hashes"], "pilot_gate": {"passed": True},
            "configuration_hash": self.manifest["configuration_hash"], "pilot_run_hash": digest(run)})
        transport = FixtureHTTP()
        with self.assertRaises(SchemaError):
            run_live_stage(self.path, "main", self.go, transport=transport)
        self.assertEqual(transport.count, 0)
        self.assertFalse((self.path / "main").exists())

    def test_fixture_cannot_qualify_for_one_interface_repeat(self):
        run_live_stage(self.path, "pilot-v1", self.go, transport=FixtureHTTP("schema"))
        with self.assertRaises(SchemaError):
            revised_pilot_manifest(self.path, "fixture test only", "NOT_REAL_APPROVAL")

    def test_stale_source_manifest_stops_before_transport(self):
        transport = FixtureHTTP()
        with patch("wgp.live.code_hashes", return_value={"changed.py": "0" * 64}):
            with self.assertRaises(SchemaError):
                run_live_stage(self.path, "pilot-v1", self.go, transport=transport)
        self.assertEqual(transport.count, 0)

    def test_cli_preflight_has_no_credential_lookup_or_network(self):
        from wgp.live_cli import main
        go_path = self.path / "fixture-go.json"
        write_new(go_path, self.go)
        original_get = os.environ.get
        def guarded_get(key, default=None):
            if key == "OPENROUTER_API_KEY":
                raise AssertionError("credential lookup")
            return original_get(key, default)
        with patch("wgp.live_cli.os.environ.get", side_effect=guarded_get):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["preflight", "--campaign", str(self.path), "--go", str(go_path),
                                       "--stage", "pilot-v1"]), 0)

    def test_wallet_changes_after_stage_are_detected_by_campaign_audit(self):
        run_live_stage(self.path, "pilot-v1", self.go, transport=FixtureHTTP())
        with BudgetLedger(self.path / "budget.jsonl", self.manifest["budget_configuration_hash"]) as ledger:
            ledger.reserve("extra-stage", "main", "request", upper_cost(fixture_config()))
        with self.assertRaises(SchemaError):
            audit_campaign(self.path, allow_fixture=True)


if __name__ == "__main__":
    unittest.main()