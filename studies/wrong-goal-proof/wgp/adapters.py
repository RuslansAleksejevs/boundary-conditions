"""Non-network adapters. A real provider requires separately authorized integration.

Each complete() call receives only one fresh request, never the case's hidden
reference AST. Synthetic doubles are software tests, not model observations.
Transcript replay consumes previously obtained responses; it makes no API call.
"""

from dataclasses import dataclass
from typing import Protocol

from .certificates import solve
from .logic import (SchemaError, canonical, keys, parse_rendered_contract,
                    strict_json, validate_contract, validate_state)


class MissingResponse(Exception):
    pass


class TransportError(Exception):
    pass


@dataclass(frozen=True)
class Reply:
    text: str
    usage: dict


class Adapter(Protocol):
    configuration: dict

    def complete(self, request: dict) -> Reply:
        ...


def parse_translation(text, expected_variables):
    result = validate_contract(strict_json(text))
    if result["variables"] != expected_variables:
        raise SchemaError("translation changed atom meanings/order")
    return result


def parse_review(text, variables):
    result = strict_json(text)
    keys(result, ("verdict", "witness"))
    if result["verdict"] not in ("SAFE", "UNSAFE", "UNRESOLVED"):
        raise SchemaError("unknown reviewer verdict")
    if result["verdict"] == "UNSAFE":
        validate_state(result["witness"], variables)
    elif result["witness"] is not None:
        raise SchemaError("SAFE/UNRESOLVED must have null witness")
    return result


def validate_usage(usage):
    keys(usage, ("input_tokens", "output_tokens", "reasoning_tokens",
                 "cached_input_tokens", "cost_usd"))
    for name in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens"):
        value = usage[name]
        if value is not None and (type(value) is not int or value < 0):
            raise SchemaError("invalid token count")
    cost = usage["cost_usd"]
    if cost is not None and (type(cost) not in (int, float) or cost < 0
                             or cost != cost or cost == float("inf")):
        raise SchemaError("invalid cost")
    return usage


UNKNOWN_USAGE = {"input_tokens": None, "output_tokens": None,
                 "reasoning_tokens": None, "cached_input_tokens": None, "cost_usd": None}


class TestDouble:
    def __init__(self, behavior="perfect"):
        if behavior not in ("perfect", "local-only", "abstain", "malformed"):
            raise ValueError("unknown synthetic double")
        self.behavior = behavior
        self.configuration = {"kind": "synthetic_test_double", "behavior": behavior,
                              "provider": None, "model": None, "new_model_calls": 0,
                              "sampling": None, "pricing": None}

    def complete(self, request):
        payload = strict_json(request["user"])
        original = parse_rendered_contract(payload["original_task"])
        if request["role"] == "translator":
            value = original
        elif self.behavior == "malformed":
            return Reply('{"verdict":"SAFE","verdict":"UNSAFE"}',
                         {**UNKNOWN_USAGE, "cost_usd": 0.0})
        elif self.behavior == "abstain":
            value = {"verdict": "UNRESOLVED", "witness": None}
        else:
            # Both doubles ignore presentation wording. Neither encodes an S win.
            certificate = (payload["certificate"] if self.behavior == "local-only"
                           else solve(original))
            value = {"verdict": certificate["verdict"],
                     "witness": certificate.get("witness")}
        return Reply(canonical(value), {**UNKNOWN_USAGE, "cost_usd": 0.0})


class TranscriptAdapter:
    """Strict prompt-bound replay; no credentials, subprocess, network, or retries.

    Entries: {id, prompt_hash, text, usage}. Metadata is fixed for the complete
    transcript. A missing entry is missing, never a simulated safe response.
    """
    def __init__(self, entries, metadata):
        keys(metadata, ("provider", "model", "model_version", "sampling", "pricing",
                        "authorization_reference"))
        for key in ("provider", "model", "authorization_reference"):
            if type(metadata[key]) is not str or not metadata[key].strip():
                raise SchemaError("transcripts need explicit model/provenance metadata")
        self.configuration = {"kind": "offline_transcript_replay", **metadata,
                              "new_model_calls": 0}
        self.entries = {}
        for entry in entries:
            keys(entry, ("id", "prompt_hash", "text", "usage"))
            if (type(entry["id"]) is not str or entry["id"] in self.entries
                    or type(entry["prompt_hash"]) is not str or type(entry["text"]) is not str):
                raise SchemaError("invalid or duplicate transcript entry")
            validate_usage(entry["usage"])
            self.entries[entry["id"]] = entry

    def complete(self, request):
        entry = self.entries.get(request["id"])
        if entry is None:
            raise MissingResponse("no recorded response")
        if entry["prompt_hash"] != request["prompt_hash"]:
            raise SchemaError("transcript is bound to a different prompt")
        return Reply(entry["text"], entry["usage"])
