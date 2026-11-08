"""Explicit OpenRouter transport and a durable, conservative per-study wallet.

No environment access occurs on import. Acquisition needs a separate preflight
GO bound to the exact configuration. Credentials and reasoning text are not logged.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from email.utils import parsedate_to_datetime
import fcntl
import hashlib
import math
from http.client import IncompleteRead, RemoteDisconnected
import os
from pathlib import Path
import signal
import socket
import threading
import time
from urllib import error, request

from .environment import strict_json
from .protocol import canonical, digest


ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
PACING_POLICY = {"minimum_start_spacing_seconds": 20, "initial_stage_pause_seconds": 20,
                 "minimum_429_cooldown_seconds": 60, "maximum_retry_after_seconds": 300,
                 "maximum_sleep_chunk_seconds": 30, "over_limit": "stop_without_retry"}
CONFIG_KEYS = {
    "schema_version", "model", "provider_slug", "response_provider", "temperature", "top_p",
    "reasoning_enabled", "stream", "max_tokens", "context_tokens", "output_reservation_tokens",
    "input_price_per_million", "output_price_per_million", "request_price_usd", "price_source", "price_as_of",
    "data_collection", "timeout_seconds", "max_request_utf8_bytes", "max_response_utf8_bytes",
    "max_summary_utf8_bytes", "budget_usd", "max_attempts", "max_technical_retries",
    "max_pilot_repeats", "version_pin_status",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def money(value):
    if type(value) not in (str, int, float, Decimal):
        raise ValueError("invalid monetary value")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid monetary value") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("money must be finite and nonnegative")
    return result


def validate_config(config):
    if type(config) is not dict or set(config) != CONFIG_KEYS:
        raise ValueError("live configuration must have exactly the documented fields")
    if (type(config["schema_version"]) is not int or config["schema_version"] != 2 or config["model"] != "qwen/qwen3.5-122b-a10b"
            or config["provider_slug"] != "alibaba" or config["response_provider"] != "Alibaba"):
        raise ValueError("only the prospectively selected model/provider is supported")
    if type(config["temperature"]) not in (int, float) or not 0 <= config["temperature"] <= 2:
        raise ValueError("invalid temperature")
    if type(config["top_p"]) not in (int, float) or not 0 < config["top_p"] <= 1:
        raise ValueError("invalid top_p")
    if type(config["reasoning_enabled"]) is not bool:
        raise ValueError("explicit reasoning enablement required; effort is not supported by this route")
    if config["stream"] is not True:
        raise ValueError("the selected thinking endpoint requires streaming acquisition")
    for name in ("max_tokens", "context_tokens", "output_reservation_tokens", "timeout_seconds",
                 "max_request_utf8_bytes", "max_response_utf8_bytes", "max_summary_utf8_bytes",
                 "max_attempts", "max_technical_retries", "max_pilot_repeats"):
        if type(config[name]) is not int or config[name] < 1:
            raise ValueError("positive integer live limits required")
    if not config["max_tokens"] <= config["output_reservation_tokens"] <= config["context_tokens"]:
        raise ValueError("output reservation must cover the requested output cap")
    if config["context_tokens"] != 262144 or config["output_reservation_tokens"] != 262144 or config["max_tokens"] > 65536:
        raise ValueError("reservation must cover the verified full native context for both input and billed output")
    if config["timeout_seconds"] > 180:
        raise ValueError("live request timeout exceeds the bounded profile")
    if config["max_attempts"] > 788 or config["max_technical_retries"] > 32 or config["max_pilot_repeats"] != 1:
        raise ValueError("study request/retry/repeat authorization exceeded")
    if money(config["budget_usd"]) > Decimal("30") or money(config["budget_usd"]) == 0:
        raise ValueError("study spending authorization is at most USD 30")
    for name in ("input_price_per_million", "output_price_per_million"):
        if money(config[name]) <= 0:
            raise ValueError("verified positive tariffs required")
    if money(config["request_price_usd"]) != 0:
        raise ValueError("the selected endpoint has no authorized per-request surcharge")
    if config["data_collection"] not in {"allow", "deny"}:
        raise ValueError("explicit data policy required")
    for name in ("price_source", "price_as_of", "version_pin_status"):
        if type(config[name]) is not str or not config[name].strip():
            raise ValueError("price provenance and model-version limitations are required")
    return config


def reservation(config):
    """Reserve the full model input context, not a guessed local token count."""
    validate_config(config)
    return (config["context_tokens"] * money(config["input_price_per_million"])
            + config["output_reservation_tokens"] * money(config["output_price_per_million"])) / Decimal(1_000_000) + money(config["request_price_usd"])


def validate_go(go, config, expected_code_hashes=None):
    if expected_code_hashes is None:
        from .runner import code_hashes
        expected_code_hashes = code_hashes()
    if (type(go) is not dict or go.get("go") is not True
            or go.get("study") != "summary-laundering"
            or go.get("configuration_hash") != digest(config)
            or go.get("code_hashes_hash") != digest(expected_code_hashes)
            or money(go.get("budget_usd")) != money(config["budget_usd"])
            or go.get("max_attempts") != config["max_attempts"]
            or not go.get("approved_at_utc") or not go.get("authorization_reference")):
        raise ValueError("coordinator preflight GO is absent or does not bind this configuration")


def wallet_hash(config):
    # A documented interface repair can adjust max_tokens within the pre-reserved
    # output bound, without resetting the campaign wallet or changing models.
    fields = ("model", "provider_slug", "response_provider", "context_tokens", "output_reservation_tokens",
              "input_price_per_million", "output_price_per_million", "request_price_usd", "budget_usd", "max_attempts", "max_technical_retries")
    return digest({key: config[key] for key in fields})


class BudgetStop(RuntimeError):
    pass


class Ledger:
    """Append-only hash chain, serialized with flock, fsynced before dispatch.

    An unresolved reservation survives restarts. It cannot be released by
    assuming a timeout was free. No same-stage restart or automatic recovery.
    """

    def __init__(self, path, config, create=False):
        self.path, self.config = Path(path), validate_config(config)
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("x", encoding="utf-8") as stream:
                self._append(stream, [], {
                    "event": "start", "configuration_hash": digest(config),
                    "wallet_hash": wallet_hash(config),
                    "budget_usd": str(money(config["budget_usd"])),
                    "max_attempts": config["max_attempts"], "max_technical_retries": config["max_technical_retries"],
                })
        with self._locked() as (_, events):
            if events[0]["wallet_hash"] != wallet_hash(config):
                raise ValueError("ledger/configuration mismatch")

    @staticmethod
    def _append(stream, events, event):
        record = {**event, "sequence": len(events), "previous_hash": events[-1]["record_hash"] if events else None,
                  "at_utc": utc_now()}
        record["record_hash"] = digest(record)
        stream.seek(0, 2)
        stream.write(canonical(record) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
        events.append(record)
        return record

    @contextmanager
    def _locked(self):
        with self.path.open("r+", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                events = [strict_json(line) for line in stream]
                audit_ledger(events, self.config)
                yield stream, events
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def start_stage(self, stage, manifest_hash, parent=None):
        with self._locked() as (stream, events):
            if stage not in {"pilot", "pilot_repair", "pilot_repair_continuation", "main"}:
                raise ValueError("unknown acquisition stage")
            if any(e["event"] == "stage_start" and e["stage"] == stage for e in events):
                raise BudgetStop("stage already started; no implicit rerun/resume")
            if audit_ledger(events, self.config)["bound_violated"]:
                raise BudgetStop("prior provider charge violated the budget bound")
            if any(e["event"] == "reserve" and not any(
                    s["event"] == "settle" and s["attempt_id"] == e["attempt_id"] for s in events) for e in events):
                raise BudgetStop("unresolved in-flight attempt; manual reconciliation required")
            record = {"event": "stage_start", "stage": stage, "manifest_hash": manifest_hash}
            if stage == "pilot_repair_continuation":
                if (type(parent) is not dict or set(parent) != {"manifest_hash", "run_hash", "ledger_tail_hash"}
                        or events[-1]["record_hash"] != parent["ledger_tail_hash"]
                        or not any(e["event"] == "stage_start" and e["stage"] == "pilot_repair"
                                   and e["manifest_hash"] == parent["manifest_hash"] for e in events)):
                    raise ValueError("continuation stage needs its exact immutable parent ledger")
                record["parent"] = parent
            elif parent is not None:
                raise ValueError("parent binding is only valid for the explicit continuation")
            self._append(stream, events, record)

    def reserve(self, attempt_id, stage, retry=False):
        with self._locked() as (stream, events):
            state = audit_ledger(events, self.config)
            if not any(e["event"] == "stage_start" and e["stage"] == stage for e in events):
                raise BudgetStop("request stage has not been explicitly started")
            if attempt_id in state["attempts"]:
                raise BudgetStop("attempt identifier already reserved")
            if state["in_flight"]:
                raise BudgetStop("only one request may be in flight")
            if state["bound_violated"]:
                raise BudgetStop("prior charge violated the conservative budget bound")
            if state["attempt_count"] >= self.config["max_attempts"]:
                raise BudgetStop("global request ceiling")
            if retry and state["retries"] >= self.config["max_technical_retries"]:
                raise BudgetStop("global technical retry ceiling")
            if stage == "pilot_repair_continuation":
                combined = sum(e["stage"] in {"pilot_repair", "pilot_repair_continuation"}
                               for e in state["attempts"].values())
                if retry or combined >= 113 or not attempt_id.startswith("pilot_repair/"):
                    raise BudgetStop("continuation cannot add retries or exceed the original 113-attempt phase cap")
            maximum = reservation(self.config)
            if state["charged_or_reserved"] + maximum > money(self.config["budget_usd"]):
                raise BudgetStop("hard monetary ceiling before dispatch")
            record = self._append(stream, events, {
                "event": "reserve", "attempt_id": attempt_id, "stage": stage,
                "retry": retry, "reserved_usd": str(maximum),
            })
            return record

    def settle(self, attempt_id, cost, status):
        with self._locked() as (stream, events):
            state = audit_ledger(events, self.config)
            if attempt_id not in state["in_flight"]:
                raise ValueError("attempt not in flight")
            amount = None if cost is None else money(cost)
            record = self._append(stream, events, {
                "event": "settle", "attempt_id": attempt_id, "status": status,
                "charged_usd": None if amount is None else str(amount),
            })
            if amount is not None and amount > reservation(self.config):
                raise BudgetStop("provider charge exceeded reserved bound; further requests prohibited")
            return record

    def snapshot(self):
        with self._locked() as (_, events):
            return events


def audit_ledger(events, config):
    if not events or events[0].get("event") != "start" or events[0].get("wallet_hash") != wallet_hash(config):
        raise ValueError("missing or mismatched ledger header")
    attempts, settled, stages = {}, {}, set()
    previous = None
    historical_charge = Decimal(0)
    in_flight = set()
    bound_violated = False
    for index, event in enumerate(events):
        if (event["sequence"] != index or event["previous_hash"] != previous
                or event["record_hash"] != digest({k: v for k, v in event.items() if k != "record_hash"})):
            raise ValueError("ledger hash chain mismatch")
        previous = event["record_hash"]
        kind = event["event"]
        if kind == "stage_start":
            if event["stage"] in stages:
                raise ValueError("repeated acquisition stage")
            if event["stage"] == "pilot_repair_continuation":
                parent = event.get("parent", {})
                if ("pilot_repair" not in stages or parent.get("ledger_tail_hash") != event["previous_hash"]
                        or not parent.get("run_hash") or not any(e["event"] == "stage_start"
                        and e["stage"] == "pilot_repair" and e["manifest_hash"] == parent.get("manifest_hash")
                        for e in events[:index])):
                    raise ValueError("unbound continuation ledger stage")
            stages.add(event["stage"])
        elif kind == "reserve":
            if event["attempt_id"] in attempts or event["stage"] not in stages or type(event["retry"]) is not bool:
                raise ValueError("invalid reservation")
            if money(event["reserved_usd"]) != reservation(config):
                raise ValueError("reservation amount mismatch")
            if event["stage"] == "pilot_repair_continuation":
                combined = sum(e["stage"] in {"pilot_repair", "pilot_repair_continuation"} for e in attempts.values())
                if event["retry"] or combined >= 113 or not event["attempt_id"].startswith("pilot_repair/"):
                    raise ValueError("continuation retries or combined attempt cap violated")
            if in_flight or bound_violated or historical_charge + reservation(config) > money(config["budget_usd"]):
                raise ValueError("reservation violated pre-dispatch budget/concurrency")
            attempts[event["attempt_id"]] = event
            historical_charge += reservation(config)
            in_flight.add(event["attempt_id"])
        elif kind == "settle":
            if event["attempt_id"] not in attempts or event["attempt_id"] in settled:
                raise ValueError("unbound/duplicate settlement")
            if event["charged_usd"] is not None:
                charge = money(event["charged_usd"])
                historical_charge += charge - reservation(config)
                bound_violated = bound_violated or charge > reservation(config) or historical_charge > money(config["budget_usd"])
            settled[event["attempt_id"]] = event
            in_flight.remove(event["attempt_id"])
        elif index != 0 or kind != "start":
            raise ValueError("unknown ledger event")
    total = sum((money(settled[key]["charged_usd"]) if key in settled and settled[key]["charged_usd"] is not None
                 else money(value["reserved_usd"]) for key, value in attempts.items()), Decimal(0))
    retries = sum(event["retry"] for event in attempts.values())
    if len(attempts) > config["max_attempts"] or retries > config["max_technical_retries"]:
        raise ValueError("ledger attempt authorization exceeded")
    return {"attempts": attempts, "settled": settled, "attempt_count": len(attempts),
            "retries": retries, "charged_or_reserved": total, "in_flight": set(attempts) - set(settled),
            "bound_violated": bound_violated}


def wire_request(messages, config):
    validate_config(config)
    return {
        "model": config["model"], "messages": messages, "stream": True,
        "stream_options": {"include_usage": True},
        "temperature": config["temperature"], "top_p": config["top_p"], "max_tokens": config["max_tokens"],
        "reasoning": {"enabled": config["reasoning_enabled"], "exclude": True},
        "provider": {
            "order": [config["provider_slug"]], "only": [config["provider_slug"]],
            "allow_fallbacks": False, "require_parameters": True,
            "data_collection": config["data_collection"],
            "max_price": {"prompt": float(money(config["input_price_per_million"])),
                          "completion": float(money(config["output_price_per_million"])),
                          "request": float(money(config["request_price_usd"]))},
        },
    }


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@contextmanager
def wall_timeout(seconds):
    """Enforce total POSIX request time, including a slowly dripped SSE line."""
    if threading.current_thread() is not threading.main_thread():
        raise ValueError("bounded HTTP acquisition requires the main thread")
    if signal.getitimer(signal.ITIMER_REAL) != (0.0, 0.0):
        raise ValueError("an existing process alarm conflicts with the HTTP wall timer")
    previous = signal.getsignal(signal.SIGALRM)

    def expired(signum, frame):
        raise TimeoutError("bounded total HTTP wall deadline")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def safe_retry_after(value, now=None):
    """Only canonical decimal seconds are retained, never arbitrary header text."""
    if type(value) is not str or len(value) > 128:
        return None
    value = value.strip()
    if value.isascii() and value.isdigit():
        return str(int(value))
    try:
        when = parsedate_to_datetime(value)
        if when.tzinfo is None:
            return None
        return str(max(0, math.ceil((when - (now or datetime.now(timezone.utc))).total_seconds())))
    except (ValueError, TypeError, OverflowError):
        return None


def cooldown_seconds(acquisition):
    value = acquisition.get("retry_after_seconds")
    if value is not None and (type(value) is not str or len(value) > 128 or not value.isascii()
                              or not value.isdigit() or str(int(value)) != value):
        raise ValueError("Retry-After must be canonical nonnegative seconds")
    if acquisition.get("http_status") != 429:
        return 0
    delay = 60 if value is None else max(60, int(value))
    return None if delay > 300 else delay


def audit_pacing(calls, stop_reason):
    previous = None
    for index, call in enumerate(calls):
        acquisition = call["acquisition"]
        start = acquisition.get("paced_attempt_started_monotonic_seconds")
        finish = acquisition.get("paced_attempt_finished_monotonic_seconds")
        if (any(type(v) not in (int, float) or not math.isfinite(v) for v in (start, finish))
                or finish < start or acquisition.get("minimum_start_spacing_seconds") != 20):
            raise ValueError("attempt spacing has invalid monotonic metadata")
        delay = cooldown_seconds(acquisition)
        expected_stop = "retry_after_over_300_seconds" if delay is None else None
        if (acquisition.get("applied_429_cooldown_seconds") != delay
                or acquisition.get("pacing_stop_reason") != expected_stop):
            raise ValueError("recorded cooldown differs from the operational policy")
        if delay is None and (index != len(calls) - 1 or stop_reason != expected_stop):
            raise ValueError("an over-limit Retry-After must halt without another attempt")
        if previous is not None:
            prior, prior_delay = previous
            if start - prior["paced_attempt_started_monotonic_seconds"] < 20:
                raise ValueError("attempt spacing is below 20 seconds")
            if prior_delay and start - prior["paced_attempt_finished_monotonic_seconds"] < prior_delay:
                raise ValueError("HTTP 429 cooldown was not respected")
        previous = (acquisition, delay)


class PacedTransport:
    """Explicit operational pacing; it never retries or changes a request."""
    kind = "openrouter_live"

    def __init__(self, backend, interval=20):
        if interval != 20:
            raise ValueError("the approved operational spacing is exactly 20 seconds")
        self.backend, self.config, self.interval = backend, backend.config, interval
        # A fresh process cannot recover another stage's monotonic origin.
        # Waiting 20s from construction conservatively separates its first call.
        self.next_start = time.monotonic() + 20
        self.blocked = False

    def send(self, payload):
        if self.blocked:
            raise ValueError("Retry-After exceeds 300 seconds; acquisition must remain stopped")
        while True:
            remaining = self.next_start - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(remaining, 30))
        started = time.monotonic()
        result = self.backend.send(payload)
        result["paced_attempt_started_monotonic_seconds"] = started
        result["paced_attempt_finished_monotonic_seconds"] = time.monotonic()
        result["minimum_start_spacing_seconds"] = self.interval
        delay = cooldown_seconds(result)
        result["applied_429_cooldown_seconds"] = delay
        result["pacing_stop_reason"] = "retry_after_over_300_seconds" if delay is None else None
        self.blocked = delay is None
        self.next_start = max(started + self.interval, result["paced_attempt_finished_monotonic_seconds"] + (delay or 0))
        return result


def visible_stream_event(body):
    """Strip reasoning and provider error text before any event is retained."""
    if type(body) is not dict:
        raise ValueError("SSE payload must be an object")
    event = {key: body.get(key) for key in ("id", "model", "provider", "usage", "created")}
    event["choices"] = []
    if "error" in body:
        event["error_code"] = body["error"].get("code") if type(body["error"]) is dict else "unknown"
    choices = body.get("choices", [])
    if type(choices) is not list:
        raise ValueError("SSE choices must be an array")
    for choice in choices:
        if type(choice) is not dict or type(choice.get("delta")) is not dict:
            raise ValueError("invalid SSE choice/delta")
        delta = choice["delta"]
        event["choices"].append({
            "index": choice.get("index"), "finish_reason": choice.get("finish_reason"),
            "native_finish_reason": choice.get("native_finish_reason"),
            "delta": {key: delta.get(key) for key in ("role", "content", "refusal")},
            "reasoning_fields_removed": any(delta.get(key) is not None for key in ("reasoning", "reasoning_details", "reasoning_content")),
            "unexpected_tool_calls": bool(delta.get("tool_calls") or delta.get("function_call")),
        })
    return event


def assemble_stream(events, done):
    """Reconstruct one completed visible answer from sanitized SSE records."""
    if not done:
        raise ValueError("SSE terminal DONE marker missing")
    identity = {key: None for key in ("id", "model", "provider", "created")}
    content, refusal = [], []
    role, finish, native_finish = None, None, None
    usage, usage_index, finish_index = None, -1, -1
    removed, tools = False, False
    for index, event in enumerate(events):
        if "error_code" in event:
            raise ValueError("SSE provider error")
        for key in identity:
            value = event.get(key)
            if value is not None:
                if identity[key] is not None and value != identity[key]:
                    raise ValueError("SSE identity changed between chunks")
                identity[key] = value
        if event.get("usage") is not None:
            usage, usage_index = event["usage"], index
        choices = event["choices"]
        if len(choices) > 1:
            raise ValueError("multiple SSE choices")
        for choice in choices:
            if type(choice["index"]) is not int or choice["index"] != 0:
                raise ValueError("unexpected SSE choice index")
            delta = choice["delta"]
            if delta.get("role") is not None:
                if delta["role"] != "assistant" or (role is not None and role != delta["role"]):
                    raise ValueError("SSE assistant role mismatch")
                role = delta["role"]
            for field, target in (("content", content), ("refusal", refusal)):
                value = delta.get(field)
                if value is not None:
                    if type(value) is not str or (finish is not None and value):
                        raise ValueError("invalid or post-finish SSE content")
                    target.append(value)
            removed = removed or choice["reasoning_fields_removed"]
            tools = tools or choice["unexpected_tool_calls"]
            if choice["finish_reason"] is not None:
                if finish is not None:
                    # Alibaba/OpenRouter repeats the terminal empty choice in
                    # its final usage chunk. Accept that one idempotent receipt,
                    # not a second answer, changed finish or continued stream.
                    if (index != len(events) - 1 or event.get("usage") is None
                            or choice["finish_reason"] != finish
                            or choice["native_finish_reason"] != native_finish
                            or delta.get("content") or delta.get("refusal")
                            or choice["unexpected_tool_calls"] or choice["reasoning_fields_removed"]):
                        raise ValueError("non-idempotent duplicate SSE terminal finish")
                else:
                    finish, native_finish, finish_index = choice["finish_reason"], choice["native_finish_reason"], index
    if finish is None or usage is None or usage_index < finish_index or role != "assistant":
        raise ValueError("SSE lacks terminal finish, final usage, or assistant role")
    return {**identity, "usage": usage, "choices": [{
        "index": 0, "finish_reason": finish, "native_finish_reason": native_finish,
        "message": {"role": role, "content": "".join(content), "refusal": "".join(refusal) or None},
        "reasoning_fields_removed": removed, "unexpected_tool_calls": tools,
    }]}


def read_sse(response, record, config, deadline, set_read_timeout):
    """Bound total bytes and wall time; hash raw bytes but retain no raw body."""
    hasher, total, data_lines = hashlib.sha256(), 0, []
    try:
        while True:
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                raise TimeoutError("bounded SSE wall time")
            set_read_timeout(remaining)
            line = response.readline(config["max_response_utf8_bytes"] - total + 1)
            if not line:
                raise ValueError("SSE stream ended without DONE")
            total += len(line)
            hasher.update(line)
            if total > config["max_response_utf8_bytes"]:
                raise ValueError("SSE byte ceiling exceeded")
            line = line.rstrip(b"\r\n")
            if line.startswith(b"data:"):
                data_lines.append(line[5:].lstrip(b" "))
            elif not line and data_lines:
                payload = b"\n".join(data_lines)
                data_lines = []
                if payload == b"[DONE]":
                    record["stream_done"] = True
                    record["visible_response"] = assemble_stream(record["stream_events"], True)
                    return
                # The unsanitized decoded event is discarded immediately.
                record["stream_events"].append(visible_stream_event(strict_json(payload.decode("utf-8"))))
            elif line and not line.startswith((b":", b"event:", b"id:", b"retry:")):
                raise ValueError("unsupported SSE field")
    finally:
        record["raw_body_sha256"] = hasher.hexdigest()
        record["response_bytes"] = total


class OpenRouterTransport:
    kind = "openrouter_live"

    def __init__(self, config, go):
        self.config = validate_config(config)
        validate_go(go, config)
        # This is the only credential lookup. No fallback names or host stores.
        self._key = os.environ.get("OPENROUTER_API_KEY")
        if not self._key:
            raise ValueError("approved OPENROUTER_API_KEY attachment is unavailable")
        self._opener = request.build_opener(NoRedirect())

    def send(self, payload):
        data = canonical(payload).encode("utf-8")
        req = request.Request(ENDPOINT, data=data, method="POST", headers={
            "Authorization": "Bearer " + self._key, "Content-Type": "application/json",
        })
        started = time.perf_counter()
        record = {"started_at_utc": utc_now(), "endpoint": ENDPOINT, "http_status": None,
                  "request_id": None, "server_date": None, "raw_body_sha256": None,
                  "visible_response": None, "technical_error": None, "retryable": False,
                  "stream_events": [], "stream_done": False, "response_bytes": 0}
        try:
            with wall_timeout(self.config["timeout_seconds"]), self._opener.open(req, timeout=self.config["timeout_seconds"]) as response:
                record.update(http_status=response.status, request_id=response.headers.get("x-request-id"),
                              server_date=response.headers.get("date"),
                              retry_after_seconds=safe_retry_after(response.headers.get("retry-after")))
                if "text/event-stream" not in response.headers.get("content-type", "").lower():
                    raise ValueError("provider did not return the requested SSE transport")
                # CPython's HTTPS response exposes the socket here. Fail closed
                # if an unsupported wrapper prevents enforcing remaining time.
                sock = getattr(getattr(getattr(response, "fp", None), "raw", None), "_sock", None)
                if sock is None:
                    raise ValueError("cannot enforce remaining SSE wall time")
                read_sse(response, record, self.config, started + self.config["timeout_seconds"], sock.settimeout)
        except error.HTTPError as exc:
            record.update(http_status=exc.code, technical_error=f"http_{exc.code}",
                          retryable=exc.code in {408, 429, 500, 502, 503, 504},
                          retry_after_seconds=safe_retry_after(exc.headers.get("retry-after") if exc.headers else None))
            exc.close()
        except (error.URLError, TimeoutError, socket.timeout, ConnectionError, IncompleteRead, RemoteDisconnected):
            record.update(technical_error="transport_failure", retryable=True)
        except (ValueError, UnicodeError, TypeError):
            record.update(technical_error="invalid_provider_stream", retryable=False, visible_response=None)
        record["finished_at_utc"] = utc_now()
        record["latency_seconds"] = time.perf_counter() - started
        return record


def visible_envelope(body):
    """Keep the exact visible content and usage, never reasoning text/headers."""
    if type(body) is not dict:
        raise ValueError("provider response must be an object")
    result = {key: body.get(key) for key in ("id", "model", "provider", "usage", "created")}
    result["choices"] = []
    choices = body.get("choices", [])
    if type(choices) is not list:
        raise ValueError("provider choices must be an array")
    for choice in choices:
        if type(choice) is not dict or type(choice.get("message", {})) is not dict:
            raise ValueError("invalid choice/message")
        message = choice.get("message", {})
        result["choices"].append({
            "index": choice.get("index"), "finish_reason": choice.get("finish_reason"),
            "native_finish_reason": choice.get("native_finish_reason"),
            "message": {key: message.get(key) for key in ("role", "content", "refusal")},
            "unexpected_tool_calls": bool(message.get("tool_calls") or message.get("function_call")),
            "reasoning_fields_removed": any(message.get(key) is not None for key in ("reasoning", "reasoning_details")),
        })
    if "error" in body:
        # Do not persist server text that could echo authorization headers.
        result["error_code"] = body["error"].get("code") if type(body["error"]) is dict else "unknown"
    return result


def inspect_response(acquisition, config):
    """Classify provider/format/usage failures separately from model outcomes."""
    technical, http_status = acquisition["technical_error"], acquisition["http_status"]
    expected_retryable = (technical == "transport_failure" or
                          (technical == f"http_{http_status}" and http_status in {408, 429, 500, 502, 503, 504}))
    if type(acquisition["retryable"]) is not bool or acquisition["retryable"] != expected_retryable:
        raise ValueError("retry eligibility contradicts recorded HTTP/error classification")
    result = {"status": "transport_error", "text": None, "usage": None, "cost_usd": None,
              "charge_for_ledger": None, "retryable": expected_retryable, "fatal": False}
    if technical:
        result["fatal"] = http_status in {401, 402, 403} or not expected_retryable
        return result
    body = acquisition["visible_response"]
    result.update(status="provider_contract_error", retryable=False, fatal=True)
    if http_status != 200 or not body or body.get("error_code") is not None:
        return result
    usage = body.get("usage")
    if type(usage) is not dict:
        return result
    prompt, completion = usage.get("prompt_tokens"), usage.get("completion_tokens")
    if any(type(v) is not int or v < 0 for v in (prompt, completion)):
        return result
    if type(usage.get("total_tokens")) is not int or usage["total_tokens"] != prompt + completion:
        return result
    details, cached = usage.get("completion_tokens_details") or {}, usage.get("prompt_tokens_details") or {}
    if type(details) is not dict or type(cached) is not dict:
        return result
    reasoning, cache = details.get("reasoning_tokens"), cached.get("cached_tokens")
    if any(v is not None and (type(v) is not int or v < 0) for v in (reasoning, cache)):
        return result
    if (reasoning is not None and reasoning > completion) or (cache is not None and cache > prompt):
        return result
    result["usage"] = {"input_tokens": prompt, "output_tokens": completion,
                       "reasoning_tokens": reasoning, "cached_input_tokens": cache}
    cost = None
    if usage.get("cost") is not None:
        try:
            cost = money(usage["cost"])
        except ValueError:
            return result
    if (prompt > config["context_tokens"] or completion > config["output_reservation_tokens"]
            or prompt + completion > config["context_tokens"]
            or body.get("model") != config["model"] or body.get("provider") != config["response_provider"]
            or type(body.get("id")) is not str or not body["id"].strip()):
        return result
    choices = body.get("choices")
    if (type(choices) is not list or len(choices) != 1
            or type(choices[0].get("index")) is not int or choices[0]["index"] != 0):
        return result
    choice = choices[0]
    if choice["message"].get("role") != "assistant" or choice.get("unexpected_tool_calls"):
        return result
    content = choice["message"].get("content")
    if content is None:
        content = ""
    if type(content) is not str:
        return result
    try:
        content.encode("utf-8")
    except UnicodeError:
        return result
    result.update(text=content, fatal=False)
    if choice["finish_reason"] == "length":
        result["status"] = "model_truncated"
    elif choice["finish_reason"] in {"content_filter", "error"} or choice["message"].get("refusal"):
        result["status"] = "model_unavailable"
    elif choice["finish_reason"] == "stop":
        result["status"] = "completed"
    else:
        result.update(status="provider_contract_error", fatal=True)
    if not result["fatal"] and cost is not None:
        # Release unused reserve only after the complete billing envelope has
        # passed route, identity, usage, cap, message and finish validation.
        # Validly billed truncation/refusal is still not a successful model task.
        result["cost_usd"] = float(cost)
        calculated = (prompt * money(config["input_price_per_million"])
                      + completion * money(config["output_price_per_million"])) / Decimal(1_000_000) + money(config["request_price_usd"])
        result["charge_for_ledger"] = max(cost, calculated)
    return result