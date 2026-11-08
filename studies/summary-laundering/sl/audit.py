"""Reject altered state scores and replay inputs before analysis."""

from collections import defaultdict

from .backends import Response, validate_response
from .data import Scenario, extract
from .environment import evaluate
from .protocol import CONDITIONS, canonical, digest, executor_request, lexical_retention, summary_request
from .runner import validate_manifest


def audit(manifest, run):
    validate_manifest(manifest, check_code=False)
    if run["manifest_hash"] != manifest["manifest_hash"] or run["evidence_label"] != manifest["evidence_label"]:
        raise ValueError("run/manifest mismatch")
    scenarios = {s["scenario_id"]: Scenario(**s) for s in manifest["scenarios"]}
    expected = {(sid, c) for sid in scenarios for c in CONDITIONS}
    actual = [(r["scenario_id"], r["condition"]) for r in run["rows"]]
    if set(actual) != expected or len(actual) != len(expected):
        raise ValueError("missing, duplicate, or extra scheduled outcome")
    summaries = {s["scenario_id"]: s for s in run["summaries"]}
    if set(summaries) != set(scenarios) or len(summaries) != len(run["summaries"]):
        raise ValueError("missing or duplicate summary")
    calls = defaultdict(list)
    expected_requests = {sid + "/summary": summary_request(s) for sid, s in scenarios.items()}
    texts_by_scenario = {}
    for sid, summary in summaries.items():
        texts = {"R": scenarios[sid].raw}
        if summary["text"] is not None:
            if summary["summary_hash"] != digest(summary["text"]):
                raise ValueError("summary hash mismatch")
            extracted, match = extract(scenarios[sid], summary["text"])
            if summary["extract"] != extracted or summary["length_match"] != match:
                raise ValueError("extract identity mismatch")
            if summary["retention"] != lexical_retention(scenarios[sid], summary["text"]):
                raise ValueError("retention annotation mismatch")
            texts.update(E=extracted, S=summary["text"])
        elif summary["summary_hash"] is not None:
            raise ValueError("missing summary has a hash")
        texts_by_scenario[sid] = texts
        for condition in CONDITIONS:
            if condition[0] in texts:
                expected_requests[sid + "/" + condition] = executor_request(scenarios[sid], condition, texts[condition[0]])
    for call in run["calls"]:
        call_id = call["call_id"]
        if call_id not in expected_requests or call["request"] != expected_requests[call_id]:
            raise ValueError("request content/role mismatch")
        if call["request_hash"] != digest({"request": call["request"], "config": manifest["config"]}):
            raise ValueError("request hash mismatch")
        if len(canonical(call["request"]).encode()) > manifest["config"]["max_request_utf8_bytes"]:
            raise ValueError("oversized request was sent")
        if call["status"] not in {"completed", "transport_error", "response_limit"}:
            raise ValueError("unknown call status")
        if call["status"] != "transport_error":
            validate_response(Response(call["text"], call["usage"], call["cost_usd"], call["model_version"]))
            if manifest["backend_kind"] == "test_double" and call["model_version"] != manifest["config"]["model_version"]:
                raise ValueError("logged model version mismatch")
            oversized = len(call["text"].encode()) > manifest["config"]["max_response_utf8_bytes"]
            if oversized != (call["status"] == "response_limit"):
                raise ValueError("response byte limit/status mismatch")
        elif any(call[k] is not None for k in ("usage", "cost_usd", "model_version")) or "text" in call:
            raise ValueError("transport failure has response metadata")
        previous = calls[call_id]
        if call["attempt"] != len(previous) or len(previous) >= 2:
            raise ValueError("invalid retry sequence")
        if previous and (previous[-1]["status"] != "transport_error" or not previous[-1]["retryable"]
                         or previous[-1]["request_hash"] != call["request_hash"]):
            raise ValueError("retry was not an identical technical retry")
        previous.append(call)
    retries = sum(len(sequence) - 1 for sequence in calls.values())
    if (retries > manifest["retry_budget"] or retries != run["retries_used"]
            or len(run["calls"]) > manifest["max_requests"] or len(run["calls"]) != run["requests_attempted"]):
        raise ValueError("request/retry budget mismatch")

    def call_status(call_id):
        sequence = calls.get(call_id, [])
        if sequence:
            return sequence[-1]["status"]
        request = expected_requests[call_id]
        if len(canonical(request).encode()) > manifest["config"]["max_request_utf8_bytes"]:
            return "context_limit"
        if len(run["calls"]) >= manifest["max_requests"]:
            return "request_budget_exhausted"
        raise ValueError("scheduled request missing without a limit")

    for sid, summary in summaries.items():
        sequence = calls.get(sid + "/summary", [])
        expected_status = call_status(sid + "/summary")
        if expected_status == "completed" and not sequence[-1]["text"].strip():
            expected_status = "empty_summary"
        if summary["status"] != expected_status:
            raise ValueError("summary status mismatch")
        if summary["text"] is not None:
            if not sequence or sequence[-1]["status"] != "completed" or sequence[-1]["text"] != summary["text"]:
                raise ValueError("summary not tied to response")
        elif expected_status == "completed":
            raise ValueError("completed summary was dropped")
        if summary["request_hash"] != digest({"request": expected_requests[sid + "/summary"], "config": manifest["config"]}):
            raise ValueError("summary request hash mismatch")
    for row in run["rows"]:
        sid, condition = row["scenario_id"], row["condition"]
        scenario, summary = scenarios[sid], summaries[sid]
        if any(row[key] != getattr(scenario, key) for key in ("cluster_id", "family", "attacked")):
            raise ValueError("scenario metadata mismatch")
        if row["summary_hash"] != summary["summary_hash"] or row["length_match"] != summary.get("length_match"):
            raise ValueError("row summary/length mismatch")
        call_id = sid + "/" + condition
        if condition[0] not in texts_by_scenario[sid]:
            if (row["status"] != "summary_unavailable" or row["score"] is not None
                    or any(row[k] is not None for k in ("request_hash", "content_hash", "gate_replay"))):
                raise ValueError("unavailable summary was scored")
            continue
        content = texts_by_scenario[sid][condition[0]]
        request_hash = digest({"request": expected_requests[call_id], "config": manifest["config"]})
        if row["content_hash"] != digest(content) or row["request_hash"] != request_hash:
            raise ValueError("replay content identity mismatch")
        sequence = calls.get(call_id, [])
        if sequence and sequence[-1]["status"] == "completed":
            expected_outcome = evaluate(sequence[-1]["text"], scenario)
            expected_gate = evaluate(sequence[-1]["text"], scenario, gate=True)
            if any(row[key] != value for key, value in expected_outcome.items()) or row["gate_replay"] != expected_gate:
                raise ValueError("score or event/state trace mismatch")
            expected_status = "completed" if expected_outcome["parse_error"] is None else "invalid_response"
            if row["status"] != expected_status:
                raise ValueError("response status mismatch")
        elif row["score"] is not None or row["gate_replay"] is not None:
            raise ValueError("technical failure was scored")
        elif row["status"] != call_status(call_id):
            raise ValueError("technical failure status mismatch")
    return {"passed": True, "scenarios": len(scenarios), "outcomes": len(actual), "calls": len(run["calls"])}