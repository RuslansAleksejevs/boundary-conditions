"""Explicit one-time operational continuation, never a replacement pilot.

The original failed run is immutable. Only its exact never-attempted suffix can
be acquired. A distinct composite record retains old calls/outcomes byte-for-byte.
"""

from copy import deepcopy
import importlib
import inspect
import os
from pathlib import Path

from .backends import Response
from .environment import strict_json
from .live_transport import PACING_POLICY, Ledger, OpenRouterTransport, PacedTransport, audit_pacing, utc_now, validate_go
from .protocol import canonical, digest
from .runner import Runner, code_hashes, revision, write_json


STAGE = "pilot_repair_continuation"
OPERATIONAL_PATHS = {"sl/continuation.py", "sl/live_run.py", "sl/live_transport.py", "sl/cli.py"}
# Captured from the repaired-pilot source before the operational amendment.
# Whole scientific modules are additionally required to remain byte-identical.
PRESERVED_FUNCTIONS = {
    "sl.live_run:fresh_cases": "e452ca17267ed2bf6ddde9714b99a10a05b2d10dcff30c42859ff04e4a987909",
    "sl.live_run:check_fixture_separation": "a7926c1cf5212ccd3a7f8878747c4189c2d2adac54874b9495dadfe058bc4dc5",
    "sl.live_run:frozen_schedule": "52a035b2cc582ef046c2921b573b2537b115500edcb326b2e274fd65329107f2",
    "sl.live_run:live_gate": "f8eac3a0d943c9e612bd6a885eeae72f90188be071fb254b40548f1421807638",
    "sl.live_transport:wire_request": "4ce5337df70313f0f145212304f6a35159fae061f5e02c9cd96e72d1f38953a5",
    "sl.live_transport:inspect_response": "8371df7511e552e633d1c922386c58271d9d4b8869f1733950c8385331da3daf",
    "sl.live_transport:assemble_stream": "8e3d0278097184a72216e206480e088d4fac8e139e34fbe322e94a7e936ee6ef",
    "sl.live_transport:visible_stream_event": "df0e41d817ea155a05a31007459586b1640cf97b2539038524d372a4cdc65d1f",
    "sl.live_transport:validate_config": "bc9df9b105778aaa17f209333dc41fc1707ed80ab169ebe5e7ab9bd9de4becf5",
    "sl.live_transport:reservation": "f6b0a0839fffb68caa88431acfcf50ecbd59e96d4da47862c72a019e10c89f8b",
}


def check_scientific_sources(old, new, check_runtime=True):
    if set(new) - set(old) - {"sl/continuation.py"} or set(old) - set(new):
        raise ValueError("unexpected source inventory change")
    if any(old.get(path) != value for path, value in new.items() if path not in OPERATIONAL_PATHS):
        raise ValueError("scientific source changed during operational amendment")
    if check_runtime:
        for name, expected in PRESERVED_FUNCTIONS.items():
            module, function = name.split(":")
            if digest(inspect.getsource(getattr(importlib.import_module(module), function))) != expected:
                raise ValueError("preserved scientific/receipt function changed: " + name)


def remaining_suffix(manifest, parent):
    schedule = [item["scenario_id"] + "/" + arm for item in manifest["schedule"]
                for arm in ["summary", *item["conditions"]]]
    attempted = {call["call_id"] for call in parent["calls"]}
    remaining = [call for call in schedule if call not in attempted]
    if (len(parent["calls"]) != 59 or len(attempted) != 54 or len(remaining) != 54
            or remaining != schedule[54:] or parent["retries_used"] != 5):
        raise ValueError("continuation is restricted to the observed 59-attempt / 54-role suffix")
    old_sids = {call.split("/")[0] for call in attempted}
    new_sids = {call.split("/")[0] for call in remaining}
    if old_sids & new_sids or len(new_sids) != 6 or sum(c.endswith("/summary") for c in remaining) != 6:
        raise ValueError("continuation must contain six wholly untouched inputs")
    return remaining


def make_continuation_plan(manifest, parent, *, fixture=False):
    from .live_run import audit_live, live_gate
    audit_live(manifest, parent)
    if (manifest["phase"] != "pilot_repair" or "continuation" in parent
            or parent["stop_reason"] != "three_consecutive_failed_logical_transports"):
        raise ValueError("only the interrupted repaired pilot may be continued once")
    if (manifest["acquisition_mode"] != "official_https") != fixture:
        raise ValueError("fixture and real continuation modes must not be mixed")
    remaining = remaining_suffix(manifest, parent)
    new_sources = code_hashes()
    check_scientific_sources(manifest["code_hashes"], new_sources)
    gate = live_gate(manifest, parent)
    plan = {
        "schema_version": 1, "study": "summary-laundering", "stage": STAGE,
        "acquisition_mode": manifest["acquisition_mode"], "created_at_utc": utc_now(),
        "code_revision": revision(), "parent_manifest_hash": manifest["manifest_hash"],
        "parent_run_hash": digest(parent), "parent_ledger_hash": digest(parent["ledger"]),
        "parent_ledger_tail_hash": parent["ledger"][-1]["record_hash"],
        "parent_ledger_length": len(parent["ledger"]), "original_code_hashes": manifest["code_hashes"],
        "code_hashes": new_sources, "preserved_functions": PRESERVED_FUNCTIONS,
        "configuration_hash": digest(manifest["config"]), "protocol_hash": manifest["protocol_hash"],
        "remaining_call_ids": remaining, "remaining_call_ids_hash": digest(remaining),
        "new_request_cap": 54, "new_retries": 0, "combined_repair_attempt_cap": 113,
        "minimum_start_spacing_seconds": 20, "maximum_sleep_chunk_seconds": 30,
        "pacing_policy": dict(PACING_POLICY),
        "wall_timeout_seconds": 180, "provider_route_exclusive": True,
        "original_gate": gate, "maximum_possible_valid_roles": gate["valid_role_responses"] + 54,
        "additional_valid_roles_needed": 98 - gate["valid_role_responses"],
        "amendment": "Operational continuation after HTTP 429; not an unchanged preregistered pilot. No attempted response can be sampled again.",
    }
    plan["plan_hash"] = digest(plan)
    return plan


def validate_plan(plan, manifest, parent, *, check_code=True):
    from .live_run import audit_live, live_gate
    audit_live(manifest, parent)
    if digest({k: v for k, v in plan.items() if k != "plan_hash"}) != plan["plan_hash"]:
        raise ValueError("continuation plan hash mismatch")
    if (plan["schema_version"] != 1 or plan["study"] != "summary-laundering" or plan["stage"] != STAGE
            or manifest["phase"] != "pilot_repair" or "continuation" in parent
            or parent["stop_reason"] != "three_consecutive_failed_logical_transports"
            or plan["acquisition_mode"] != manifest["acquisition_mode"]):
        raise ValueError("invalid continuation parent/mode")
    remaining = remaining_suffix(manifest, parent)
    if (plan["parent_manifest_hash"] != manifest["manifest_hash"] or plan["parent_run_hash"] != digest(parent)
            or plan["parent_ledger_hash"] != digest(parent["ledger"])
            or plan["parent_ledger_tail_hash"] != parent["ledger"][-1]["record_hash"]
            or plan["parent_ledger_length"] != len(parent["ledger"])
            or plan["configuration_hash"] != digest(manifest["config"])
            or plan["protocol_hash"] != manifest["protocol_hash"]
            or plan["original_code_hashes"] != manifest["code_hashes"]
            or plan["remaining_call_ids"] != remaining or plan["remaining_call_ids_hash"] != digest(remaining)):
        raise ValueError("continuation changed its parent, configuration, or untouched suffix")
    if (plan["new_request_cap"] != 54 or plan["new_retries"] != 0 or plan["combined_repair_attempt_cap"] != 113
            or plan["minimum_start_spacing_seconds"] != 20 or plan["maximum_sleep_chunk_seconds"] != 30
            or plan["wall_timeout_seconds"] != 180 or plan["provider_route_exclusive"] is not True
            or plan["pacing_policy"] != PACING_POLICY
            or plan["preserved_functions"] != PRESERVED_FUNCTIONS):
        raise ValueError("continuation operational caps changed")
    gate = live_gate(manifest, parent)
    if (plan["original_gate"] != gate or plan["maximum_possible_valid_roles"] != gate["valid_role_responses"] + 54
            or plan["additional_valid_roles_needed"] != 98 - gate["valid_role_responses"]):
        raise ValueError("continuation altered the original gate")
    check_scientific_sources(plan["original_code_hashes"], plan["code_hashes"], check_runtime=check_code)
    if check_code and plan["code_hashes"] != code_hashes():
        raise ValueError("code changed since continuation plan")


def validate_continuation_go(go, plan, config):
    validate_go(go, config, plan["code_hashes"])
    if (go.get("continuation_plan_hash") != plan["plan_hash"]
            or go.get("provider_route_exclusive") is not True):
        raise ValueError("GO must explicitly bind this continuation and exclusive provider route")


def audit_continuation_binding(manifest, composite):
    """Run before the shared state/receipt audit; no scientific metrics change."""
    extension = composite["continuation"]
    if extension.get("record_kind") != "amended_composite_not_original_run":
        raise ValueError("continuation must be explicitly labeled as a composite")
    plan, parent = extension["plan"], extension["parent_run"]
    validate_plan(plan, manifest, parent, check_code=False)
    validate_continuation_go(extension["preflight_go"], plan, manifest["config"])
    if composite["preflight_go"] != parent["preflight_go"]:
        raise ValueError("original pilot authorization was replaced")
    old_count = len(parent["calls"])
    new_calls = composite["calls"][old_count:]
    if (canonical(composite["calls"][:old_count]) != canonical(parent["calls"])
            or canonical(composite["ledger"][:len(parent["ledger"])]) != canonical(parent["ledger"])
            or len(new_calls) > 54 or len(composite["calls"]) > 113 or composite["retries_used"] != 5):
        raise ValueError("continuation rewrote old calls/wallet or exceeded combined limits")
    remaining = set(plan["remaining_call_ids"])
    untouched = {call.split("/")[0] for call in remaining}
    for key in ("rows", "summaries"):
        old = [r for r in parent[key] if r["scenario_id"] not in untouched]
        current = [r for r in composite[key] if r["scenario_id"] not in untouched]
        if canonical(current) != canonical(old):
            raise ValueError("continuation changed previously attempted outcomes or summaries")
    stages = [e for e in composite["ledger"] if e["event"] == "stage_start" and e["stage"] == STAGE]
    expected_parent = {"manifest_hash": manifest["manifest_hash"], "run_hash": digest(parent),
                       "ledger_tail_hash": parent["ledger"][-1]["record_hash"]}
    if len(stages) != 1 or stages[0]["manifest_hash"] != plan["plan_hash"] or stages[0].get("parent") != expected_parent:
        raise ValueError("continuation stage is not bound to the exact plan and parent")
    reserved = {e["attempt_id"]: e for e in composite["ledger"] if e["event"] == "reserve"}
    for call in new_calls:
        if call["call_id"] not in remaining or call["attempt"] != 0 or reserved[call["attempt_id"]]["stage"] != STAGE:
            raise ValueError("continuation sampled an attempted role or added a retry")
    audit_pacing(new_calls, composite["stop_reason"])
    new_attempt_ids = {call["attempt_id"] for call in new_calls}
    if {key for key, event in reserved.items() if event["stage"] == STAGE} != new_attempt_ids:
        raise ValueError("continuation ledger contains an unlogged attempt")
    return {"pilot_repair", STAGE}


def effective_pilot_sources(manifest, run):
    if "continuation" in run:
        audit_continuation_binding(manifest, run)
        return run["continuation"]["plan"]["code_hashes"]
    return manifest["code_hashes"]


class ContinuationRunner:
    """Use the unchanged Runner for replay and LiveRunner for new acquisition."""

    def __init__(self, manifest, parent, plan, backend, ledger, go, emit=None):
        validate_plan(plan, manifest, parent)
        validate_continuation_go(go, plan, manifest["config"])
        if backend.config != manifest["config"] or ledger.config != manifest["config"]:
            raise ValueError("continuation transport/wallet configuration changed")
        if ledger.snapshot() != parent["ledger"]:
            raise ValueError("continuation must begin at the exact preserved ledger prefix")
        self.manifest, self.parent, self.plan = manifest, parent, plan
        self.backend, self.ledger, self.go = backend, ledger, go
        self.config, self.emit = manifest["config"], emit or (lambda record: None)
        self.calls, self.retries_used = deepcopy(parent["calls"]), parent["retries_used"]
        self.previous = {}
        for call in parent["calls"]:
            self.previous[call["call_id"]] = call
        self.remaining = set(plan["remaining_call_ids"])
        self.provider_ids = {c["acquisition"]["visible_response"]["id"] for c in parent["calls"]
                             if c["acquisition"].get("visible_response")}
        self.stop_reason, self.consecutive_transport_failures = None, 0
        self.ledger_stage = STAGE

    def call(self, request, call_id):
        from .live_run import LiveRunner
        request_hash = digest({"request": request, "config": self.config})
        if call_id in self.previous:
            call = self.previous[call_id]
            if call["request"] != request or call["request_hash"] != request_hash:
                raise ValueError("attempted request changed during deterministic replay")
            if call["status"] != "completed":
                return None, call["status"], request_hash
            if request["role"] == "summarizer" and len(call["text"].encode()) > self.config["max_summary_utf8_bytes"]:
                return None, "summary_limit", request_hash
            return Response(call["text"], call["usage"], call["cost_usd"], call["model_version"]), "completed", request_hash
        if call_id not in self.remaining:
            raise ValueError("role is not in the frozen untouched suffix")
        if len(self.calls) >= 113:
            self.stop_reason = "combined_repair_attempt_cap"
            return None, "acquisition_stopped", request_hash
        return LiveRunner.call(self, request, call_id)

    def run(self):
        from .live_run import audit_live
        parent_binding = {"manifest_hash": self.manifest["manifest_hash"], "run_hash": digest(self.parent),
                          "ledger_tail_hash": self.parent["ledger"][-1]["record_hash"]}
        self.ledger.start_stage(STAGE, self.plan["plan_hash"], parent=parent_binding)
        result = Runner.run(self)
        result.update(phase="pilot_repair", acquisition_mode=self.manifest["acquisition_mode"],
                      preflight_go=self.parent["preflight_go"], ledger=self.ledger.snapshot(),
                      stop_reason=self.stop_reason, completed_at_utc=utc_now(),
                      continuation={"plan": self.plan, "parent_run": self.parent, "preflight_go": self.go,
                                    "record_kind": "amended_composite_not_original_run"})
        audit_live(self.manifest, result)
        return result


def acquire_continuation(parent_path, plan_path, go_path, ledger_path, out):
    from .live_run import audit_live, live_gate
    parent_path = Path(parent_path)
    manifest = strict_json((parent_path / "manifest.json").read_text(encoding="utf-8"))
    parent = strict_json((parent_path / "run.json").read_text(encoding="utf-8"))
    plan = strict_json(Path(plan_path).read_text(encoding="utf-8"))
    go = strict_json(Path(go_path).read_text(encoding="utf-8"))
    validate_plan(plan, manifest, parent)
    if plan["acquisition_mode"] != "official_https":
        raise ValueError("a continuation fixture cannot acquire real observations")
    validate_continuation_go(go, plan, manifest["config"])
    ledger = Ledger(ledger_path, manifest["config"])
    if ledger.snapshot() != parent["ledger"]:
        raise ValueError("continuation ledger changed since the original stop")
    backend = PacedTransport(OpenRouterTransport(manifest["config"], go))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "manifest.json", manifest)
    write_json(out / "continuation_plan.json", plan)
    with (out / "events.jsonl").open("x", encoding="utf-8") as stream:
        def emit(record):
            stream.write(canonical(record) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        emit({"record_type": "continuation_header", "plan_hash": plan["plan_hash"],
              "old_calls_replayed_locally": len(parent["calls"]), "new_calls_only_in_this_event_log": True})
        run = ContinuationRunner(manifest, parent, plan, backend, ledger, go, emit=emit).run()
    write_json(out / "run.json", run)
    write_json(out / "audit.json", audit_live(manifest, run))
    write_json(out / "pilot_gate.json", {"amended_composite_gate": live_gate(manifest, run),
                                       "immutable_original_gate": plan["original_gate"]})
    return manifest, run