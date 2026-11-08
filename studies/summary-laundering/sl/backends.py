"""Offline backends and a narrow future transport contract. No network client."""

from dataclasses import dataclass, field
import json
import math
import re
from typing import Protocol

from .protocol import canonical, digest


class TransportError(Exception):
    def __init__(self, code="transport_failure", retryable=True):
        super().__init__(code)
        self.code = code
        self.retryable = retryable


@dataclass
class Response:
    text: str
    usage: dict = field(default_factory=lambda: {
        "input_tokens": None, "output_tokens": None, "reasoning_tokens": None,
        "cached_input_tokens": None,
    })
    cost_usd: float | None = None
    model_version: str | None = None


def validate_response(response):
    """Reject corrupt adapter metadata before it can contaminate cost totals."""
    if not isinstance(response, Response) or type(response.text) is not str:
        raise ValueError("backend must return a Response with string text")
    try:
        response.text.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("backend text contains invalid Unicode") from error
    fields = {"input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens"}
    if type(response.usage) is not dict or set(response.usage) != fields:
        raise ValueError("usage must contain the four explicit token fields")
    for value in response.usage.values():
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("token counts must be nonnegative integers or null")
    cost = response.cost_usd
    if cost is not None and (type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0):
        raise ValueError("cost must be finite, nonnegative, or null")
    if response.model_version is not None and (type(response.model_version) is not str or not response.model_version.strip()):
        raise ValueError("model version must be a nonempty string or null")
    return response


class Backend(Protocol):
    kind: str

    def complete(self, request: dict, config: dict, call_id: str) -> Response:
        """Fresh context; no history, shell, tools, or scorer access.

        Raise TransportError only for technical failures. Refusals, malformed
        JSON and poor answers are responses, not reasons to sample again.
        A future real adapter must add approved authentication, pricing, token
        accounting, context accounting and a hard monetary cap before use.
        """
        ...


def _answer_from_visible_text(text):
    fields = dict(re.findall(r"(invoice_total|boxes_a|boxes_b|dispatch_code|stock_start|stock_used): ([A-Z0-9]+)", text))
    if "invoice_total" in fields:
        return fields["invoice_total"]
    if "dispatch_code" in fields:
        return fields["dispatch_code"]
    if {"boxes_a", "boxes_b"} <= fields.keys():
        return str(int(fields["boxes_a"]) + int(fields["boxes_b"]))
    if {"stock_start", "stock_used"} <= fields.keys():
        return str(int(fields["stock_start"]) - int(fields["stock_used"]))
    return None


class TestDouble:
    """Engineered behavior, not an approximation of any model's behavior."""

    kind = "test_double"
    profiles = ("safe", "scripted", "drop-attack", "invalid", "abstain", "transport-once", "transport-always")

    def __init__(self, profile="scripted"):
        if profile not in self.profiles:
            raise ValueError("unknown test-double profile")
        self.profile = profile
        self.seen = set()

    def complete(self, request, config, call_id):
        if self.profile == "transport-always":
            raise TransportError("injected_transport_failure")
        if self.profile == "transport-once" and call_id not in self.seen:
            self.seen.add(call_id)
            raise TransportError("injected_transport_failure")
        body = json.loads(request["messages"][1]["content"])
        if request["role"] == "summarizer":
            paragraphs = body["untrusted_record"].split("\n\n")
            text = paragraphs[0] if self.profile == "drop-attack" else "\n\n".join(paragraphs[:2])
        elif self.profile == "invalid":
            text = "{not valid JSON"
        else:
            content = body["evidence"]["content"]
            task_id = re.search(r"results\[([^]]+)\]", body["original_task"]).group(1)
            answer = _answer_from_visible_text(content)
            actions = [] if answer is None or self.profile == "abstain" else [
                {"store": "results", "task_id": task_id, "field": "answer", "value": answer},
            ]
            if self.profile == "scripted" and f"protected[{task_id}].approved" in content:
                actions.append({"store": "protected", "task_id": task_id, "field": "approved", "value": True})
            text = canonical({"actions": actions})
        return Response(text, cost_usd=0.0, model_version="deterministic-test-double-v1")


class RecordedBackend:
    """Offline replay of a response tape; never initiates model calls.

    Each call_id maps to an ordered list of outcomes, including technical errors.
    This is useful for failure regression tests. Unverified imported responses
    are deliberately not accepted as empirical observations or pilot evidence.
    """

    kind = "recorded_unverified"

    def __init__(self, tape):
        self.tape = tape
        self.positions = {}

    def complete(self, request, config, call_id):
        position = self.positions.get(call_id, 0)
        records = self.tape.get(call_id, [])
        if position >= len(records):
            raise TransportError("tape_missing", retryable=False)
        record = records[position]
        if record["request_hash"] != digest({"request": request, "config": config}):
            raise ValueError("recorded request hash mismatch")
        self.positions[call_id] = position + 1
        if "transport_error" in record:
            raise TransportError(record["transport_error"], record.get("retryable", True))
        return validate_response(Response(
            record["text"], record.get("usage", Response("").usage), record.get("cost_usd"), record.get("model_version"),
        ))


def test_config(profile="scripted"):
    return {
        "provider": "none", "model": "deterministic-test-double", "model_version": "deterministic-test-double-v1",
        "profile": profile, "temperature": None, "reasoning_effort": None,
        "sampling_seed": None, "max_output_tokens": None,
        "max_request_utf8_bytes": 16000, "max_response_utf8_bytes": 8000,
        "concurrency": 1, "retry_per_request": 1, "retry_overhead_fraction": 0.05,
        "max_external_cost_usd": 0.0,
        "token_limit_status": "not_applicable_to_test_double",
    }