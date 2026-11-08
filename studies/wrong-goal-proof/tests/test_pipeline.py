import copy
import unittest

from wgp.adapters import (Reply, TestDouble, TranscriptAdapter, TransportError,
                          UNKNOWN_USAGE, parse_review, parse_translation, validate_usage)
from wgp.analysis import analyze, paired, summarize, wilson
from wgp.certificates import verify
from wgp.dataset import make_dataset
from wgp.logic import SchemaError, canonical, digest, op, parse_rendered_contract, strict_json
from wgp.pipeline import audit_run, pilot_gate, run_pipeline
from wgp.prompts import HEADINGS, review_request
from wgp.vector import witness_valid


METADATA = {"provider": "fixture", "model": "not-a-model", "model_version": None,
            "sampling": None, "pricing": None, "authorization_reference": "unit-test-only"}


class InterfaceTests(unittest.TestCase):
    def test_review_schema(self):
        bad = [{"verdict": "PASS", "witness": None}, {"verdict": "SAFE"},
               {"verdict": "UNSAFE", "witness": None},
               {"verdict": "SAFE", "witness": {"p": True}},
               {"verdict": "UNRESOLVED", "witness": None, "rationale": "extra"},
               {"verdict": "UNSAFE", "witness": {"p": 1}}]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(SchemaError):
                parse_review(canonical(value), ["p"])

    def test_valid_review_unsafety_requires_complete_witness(self):
        value = {"verdict": "UNSAFE", "witness": {"p": True, "q": False}}
        self.assertEqual(parse_review(canonical(value), ["p", "q"]), value)

    def test_translation_must_preserve_variable_set(self):
        with self.assertRaises(SchemaError):
            parse_translation('{"variables":["p"],"C":{"var":"p"},"Q":{"var":"p"}}',
                              ["p", "q"])

    def test_usage_unknown_not_zero(self):
        self.assertIsNone(validate_usage(UNKNOWN_USAGE)["cost_usd"])

    def test_usage_strict_counts(self):
        for value in (-1, True, 1.5, "100"):
            with self.subTest(value=value), self.assertRaises(SchemaError):
                validate_usage({**UNKNOWN_USAGE, "input_tokens": value})
        for value in (float("nan"), float("inf"), -1, True):
            with self.subTest(value=value), self.assertRaises(SchemaError):
                validate_usage({**UNKNOWN_USAGE, "cost_usd": value})

    def test_transcript_rejects_duplicate_entries(self):
        entry = {"id": "a", "prompt_hash": "h", "text": "{}", "usage": UNKNOWN_USAGE}
        with self.assertRaises(SchemaError):
            TranscriptAdapter([entry, entry], METADATA)

    def test_transcript_needs_provenance(self):
        with self.assertRaises(SchemaError):
            TranscriptAdapter([], {**METADATA, "authorization_reference": ""})


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = make_dataset()
        cls.perfect = run_pipeline(cls.data, "dev", TestDouble("perfect"), "fixture-manifest")
        cls.local = run_pipeline(cls.data, "dev", TestDouble("local-only"), "fixture-manifest")

    def test_planned_dev_counts(self):
        self.assertEqual(len(self.perfect["calls"]), 52)
        self.assertEqual(len(self.perfect["outcomes"]), 44)
        self.assertEqual(self.perfect["new_model_calls"], 0)
        self.assertTrue(all(o["correct"] for o in self.perfect["outcomes"]))

    def test_planned_holdout_counts(self):
        run = run_pipeline(self.data, "holdout", TestDouble("perfect"), "fixture-manifest")
        self.assertEqual(run["scheduled_calls"], 260)
        self.assertEqual(len(run["outcomes"]), 220)
        self.assertTrue(all(o["correct"] for o in run["outcomes"]))

    def test_faults_not_counted_as_natural_drift(self):
        report = analyze(self.local)
        self.assertEqual(report["natural_drift_among_valid_translations"]["numerator"], 0)
        self.assertEqual(report["groups"]["natural"]["B"]["correct_completion"]["numerator"], 8)
        for arm in ("B", "N", "S"):
            self.assertEqual(report["groups"]["fault"][arm]["observed_false_safe_all_scheduled"]["numerator"], 8)

    def test_each_false_guarantee_has_valid_local_certificate_and_independent_witness(self):
        originals = {c["id"]: c["original"] for c in self.data["splits"]["dev"]}
        failed = [o for o in self.local["outcomes"] if o["false_safe"]]
        self.assertEqual(len(failed), 24)
        for outcome in failed:
            self.assertTrue(verify(outcome["candidate"], outcome["certificate"])["valid"])
            evidence = outcome["false_assurance_evidence"]
            self.assertTrue(evidence["scalar_confirmed"] and evidence["vector_confirmed"])
            self.assertTrue(witness_valid(originals[outcome["case_id"]], evidence["witness"]))

    def test_same_evidence_all_arms_only_presentation_changes(self):
        for case in self.data["splits"]["dev"]:
            if case["group"] == "natural":
                continue
            requests = [review_request(case, case["candidate"], case["certificate"], arm)
                        for arm in ("B", "N", "S")]
            self.assertEqual(len({r["system"] for r in requests}), 1)
            payloads = [strict_json(r["user"]) for r in requests]
            for payload in payloads:
                payload.pop("presentation")
                self.assertEqual(payload["original_task"], case["task"])
                self.assertNotIn("original", payload)
                self.assertNotIn("family", payload)
            self.assertEqual(payloads[0], payloads[1])
            self.assertEqual(payloads[1], payloads[2])

    def test_headings_approximately_character_matched_not_token_claim(self):
        lengths = list(map(len, HEADINGS.values()))
        self.assertLess(max(lengths) - min(lengths), 20)
        self.assertIn("PASS", HEADINGS["B"])
        self.assertNotIn("PASS", HEADINGS["N"])

    def test_perfect_and_local_doubles_do_not_encode_scoped_advantage(self):
        for run in (self.perfect, self.local):
            comparison = analyze(run)["primary_fault_S_minus_B"]
            self.assertEqual(comparison["difference"], 0)
            self.assertEqual(comparison["complete_pairs"], 8)

    def test_equivalent_controls_show_textual_gate_false_rejection(self):
        controls = [o for o in self.perfect["outcomes"] if o["group"] == "equivalent"]
        self.assertTrue(all(o["oracle_ceiling"]["certificate_bound_to_original"] for o in controls))
        self.assertTrue(all(not o["oracle_ceiling"]["textual_identity"] for o in controls))

    def test_abstention_is_not_correct_or_accepted(self):
        run = run_pipeline(self.data, "dev", TestDouble("abstain"), "fixture-manifest")
        self.assertTrue(all(o["abstained"] and not o["correct"] and not o["accepted"] for o in run["outcomes"]))
        self.assertFalse(pilot_gate(self.data, run)["passed"])
        self.assertIsNone(analyze(run)["groups"]["fault"]["B"]["error_among_accepted"]["estimate"])

    def test_schema_errors_not_successes_or_drift(self):
        run = run_pipeline(self.data, "dev", TestDouble("malformed"), "fixture-manifest")
        self.assertTrue(all(o["status"] == "schema_error" for o in run["outcomes"]))
        report = analyze(run)
        self.assertEqual(report["groups"]["fault"]["B"]["unassessed"], 8)
        self.assertEqual(report["groups"]["fault"]["B"]["full_sample_false_safe_bounds"], [0, 1])
        self.assertFalse(pilot_gate(self.data, run)["passed"])

    def test_missing_translations_block_dependent_reviews(self):
        run = run_pipeline(self.data, "dev", TranscriptAdapter([], METADATA), "fixture-manifest")
        report = analyze(run)
        self.assertEqual(report["call_statuses"], {"missing": 44, "blocked_translation": 8})
        self.assertEqual(report["adapter_invocations"], 44)
        self.assertEqual(report["primary_fault_S_minus_B"]["complete_pairs"], 0)
        self.assertIsNone(report["usage"]["cost_usd"]["total"])
        natural = [o for o in run["outcomes"] if o["group"] == "natural"]
        self.assertTrue(all(o["fidelity"] is None for o in natural))

    def test_invalid_translations_record_schema_not_semantic_drift(self):
        class BadTranslator(TestDouble):
            def complete(self, req):
                if req["role"] == "translator":
                    return Reply("not-json", UNKNOWN_USAGE)
                return super().complete(req)
        run = run_pipeline(self.data, "dev", BadTranslator(), "fixture-manifest")
        natural = [o for o in run["outcomes"] if o["group"] == "natural"]
        self.assertTrue(all(o["fidelity"] is None and o["translation_status"] == "schema_error" for o in natural))

    def test_scripted_translation_drift_distinct_from_original_truth(self):
        class DriftingTranslator(TestDouble):
            def complete(self, req):
                if req["role"] == "translator":
                    original = parse_rendered_contract(strict_json(req["user"])["original_task"])
                    candidate = {**original, "C": op("and", original["C"], original["Q"])}
                    return Reply(canonical(candidate), UNKNOWN_USAGE)
                return super().complete(req)
        run = run_pipeline(self.data, "dev", DriftingTranslator(), "fixture-manifest")
        natural = [o for o in run["outcomes"] if o["group"] == "natural"]
        self.assertGreater(sum(not o["fidelity"]["open_functions_equal"] for o in natural), 0)
        self.assertTrue(all(o["correct"] for o in natural))

    def test_transport_errors_no_retries(self):
        class BrokenTransport(TestDouble):
            def __init__(self):
                super().__init__()
                self.attempts = 0
            def complete(self, request):
                self.attempts += 1
                raise TransportError("synthetic timeout")
        adapter = BrokenTransport()
        run = run_pipeline(self.data, "dev", adapter, "fixture-manifest")
        self.assertEqual(adapter.attempts, 44)
        self.assertEqual(sum(c["status"] == "transport_error" for c in run["calls"]), 44)

    def test_transcript_replay_same_outcomes(self):
        entries = [{"id": c["request"]["id"], "prompt_hash": c["request"]["prompt_hash"],
                    "text": c["response_text"], "usage": c["usage"]} for c in self.local["calls"]]
        replay = run_pipeline(self.data, "dev", TranscriptAdapter(entries, METADATA), "fixture-manifest")
        self.assertEqual(replay["outcomes"], self.local["outcomes"])
        self.assertEqual(replay["new_model_calls"], 0)

    def test_wrong_prompt_hash_not_silently_replayed(self):
        c = next(c for c in self.perfect["calls"] if c["request"]["role"] == "translator")
        adapter = TranscriptAdapter([{"id": c["request"]["id"], "prompt_hash": "wrong",
                                      "text": c["response_text"], "usage": c["usage"]}], METADATA)
        run = run_pipeline(self.data, "dev", adapter, "fixture-manifest")
        record = next(x for x in run["calls"] if x["request"]["id"] == c["request"]["id"])
        self.assertEqual(record["status"], "schema_error")

    def test_audit_rejects_missing_or_duplicate_calls_and_outcomes(self):
        for field in ("calls", "outcomes"):
            for duplicate in (False, True):
                run = copy.deepcopy(self.perfect)
                if duplicate:
                    run[field][-1] = copy.deepcopy(run[field][0])
                else:
                    run[field].pop()
                with self.subTest(field=field, duplicate=duplicate), self.assertRaises(SchemaError):
                    audit_run(self.data, run)

    def test_audit_rejects_fabricated_score_or_counterexample(self):
        for field in ("score", "evidence"):
            run = copy.deepcopy(self.local)
            outcome = next(o for o in run["outcomes"] if o["false_safe"])
            if field == "score":
                outcome["false_safe"] = False
            else:
                outcome["false_assurance_evidence"]["witness"]["p"] = "fake"
            with self.assertRaises(SchemaError):
                audit_run(self.data, run)

    def test_audit_rejects_edited_raw_response_or_prompt(self):
        for field in ("response_text", "request"):
            run = copy.deepcopy(self.perfect)
            record = next(c for c in run["calls"] if c["request"]["role"] == "reviewer")
            if field == "response_text":
                record[field] = '{"verdict":"UNRESOLVED","witness":null}'
            else:
                record["request"]["user"] += " extra hidden instruction"
            with self.assertRaises(SchemaError):
                audit_run(self.data, run)

    def test_audit_rejects_response_hidden_under_transport_failure(self):
        run = copy.deepcopy(self.perfect)
        record = next(c for c in run["calls"] if c["request"]["role"] == "reviewer")
        record["status"] = "transport_error"
        record["parsed"] = None
        with self.assertRaises(SchemaError):
            audit_run(self.data, run)

    def test_audit_rejects_wrong_invocation_latency_and_boolean_types(self):
        for change in ("invocation", "latency", "score", "model_calls"):
            run = copy.deepcopy(self.perfect)
            if change == "invocation":
                run["calls"][0]["adapter_invoked"] = False
            elif change == "latency":
                run["calls"][0]["latency_seconds"] = -1
            elif change == "score":
                run["outcomes"][0]["correct"] = 1
            else:
                run["new_model_calls"] = 260
            with self.subTest(change=change), self.assertRaises(SchemaError):
                audit_run(self.data, run)

    def test_incremental_journal_has_every_call_and_outcome(self):
        events = []
        run_pipeline(self.data, "dev", TestDouble(), "fixture-manifest", emit=events.append)
        self.assertEqual(events[0]["event"], "run_start")
        self.assertEqual(events[-1]["event"], "run_end")
        self.assertEqual(sum(e["event"] == "call" for e in events), 52)
        self.assertEqual(sum(e["event"] == "outcome" for e in events), 44)

    def test_pilot_clean_case_denominator_not_three_independent_controls(self):
        gate = pilot_gate(self.data, self.local)
        self.assertTrue(gate["passed"])
        self.assertEqual(gate["valid_responses"], 52)
        self.assertEqual(gate["clean_cases"], 12)
        self.assertEqual(gate["clean_cases_correct_in_all_conditions"], 12)


class StatisticsTests(unittest.TestCase):
    def test_wilson_zero_has_nonzero_uncertainty(self):
        low, high = wilson(0, 40)
        self.assertAlmostEqual(low, 0)
        self.assertGreater(high, 0.08)

    def test_wilson_empty_is_not_zero(self):
        self.assertIsNone(wilson(0, 0))

    def test_paired_contract_resampling_and_direction(self):
        outcomes = []
        for i in range(40):
            outcomes.extend([{"case_id": str(i), "condition": "B", "status": "completed", "false_safe": True},
                             {"case_id": str(i), "condition": "S", "status": "completed", "false_safe": False}])
        result = paired(outcomes, "S")
        self.assertEqual(result["complete_pairs"], 40)
        self.assertEqual(result["difference"], -1)
        self.assertEqual(result["sum_differences"], -40)
        self.assertEqual(result["discordance"], {"B=1,S=0": 40})
        self.assertEqual(result, paired(outcomes, "S"))

    def test_incomplete_pairs_are_not_zero_imputed(self):
        result = paired([{"case_id": "a", "condition": "B", "status": "completed", "false_safe": True},
                         {"case_id": "a", "condition": "S", "status": "missing", "false_safe": False}], "S")
        self.assertEqual(result["complete_pairs"], 0)
        self.assertIsNone(result["difference"])
        self.assertEqual(result["scheduled_difference_bounds"], [-1, 0])

    def test_zero_discordance_conservative_interval_not_degenerate(self):
        outcomes = [{"case_id": str(i), "condition": arm, "status": "completed", "false_safe": False}
                    for i in range(40) for arm in ("B", "S")]
        result = paired(outcomes, "S")
        self.assertEqual(result["bootstrap95"], [0, 0])
        self.assertLess(result["bounded_iid_hoeffding95"][0], 0)
        self.assertGreater(result["bounded_iid_hoeffding95"][1], 0)


if __name__ == "__main__":
    unittest.main()
