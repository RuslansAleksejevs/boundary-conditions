"""Small official OpenRouter transport with explicit routing and receipt checks.

No transport instance is created by offline commands. Credentials are provided
only at authorized execution time, never serialized, printed, or read from disk.
"""

import copy
import time
import urllib.error
import urllib.request
from decimal import Decimal

from .adapters import UNKNOWN_USAGE
from .live_budget import money
from .logic import SchemaError, canonical, digest, keys, strict_json
from .pipeline import timestamp


ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
PROVIDER = "together"


def validate_configuration(config):
    keys(config, ("version", "model", "provider_slug", "provider_response_name",
                  "temperature", "top_p", "reasoning_effort", "max_tokens", "output_reservation_tokens",
                  "context_token_bound", "max_request_bytes", "timeout_seconds",
                  "input_usd_per_million", "output_usd_per_million", "request_usd",
                  "price_source", "price_as_of", "quota_usd", "data_collection", "version_pin_status"))
    if (type(config["version"]) is not int or config["version"] != 1
            or config["model"] != MODEL or config["provider_slug"] != PROVIDER
            or type(config["provider_response_name"]) is not str
            or not config["provider_response_name"].strip()):
        raise SchemaError("unapproved model/provider configuration")
    for name in ("max_tokens", "output_reservation_tokens", "context_token_bound", "max_request_bytes", "timeout_seconds"):
        if type(config[name]) is not int or config[name] < 1:
            raise SchemaError("positive integer live limit required")
    if (not config["max_tokens"] <= config["output_reservation_tokens"] < config["context_token_bound"]
            or config["timeout_seconds"] > 60 or config["max_request_bytes"] > 200_000):
        raise SchemaError("unsupported live caps")
    for name, low, high in (("temperature", 0, 2), ("top_p", 0, 1)):
        value = config[name]
        if type(value) not in (int, float) or not low <= value <= high or (name == "top_p" and value == 0):
            raise SchemaError("unsupported sampling parameter")
    if config["reasoning_effort"] not in ("low", "medium", "high"):
        raise SchemaError("explicit supported reasoning effort required")
    if (config["data_collection"] not in ("allow", "deny")
            or type(config["version_pin_status"]) is not str or not config["version_pin_status"].strip()):
        raise SchemaError("explicit provider data policy and model-version limitation required")
    for name in ("input_usd_per_million", "output_usd_per_million", "request_usd", "quota_usd"):
        money(config[name])
    if money(config["quota_usd"]) != Decimal("20"):
        raise SchemaError("wrong per-study quota")
    if not str(config["price_source"]).startswith("https://") or not config["price_as_of"]:
        raise SchemaError("dated official price source required")
    if upper_cost(config) * 379 > Decimal("20"):
        raise SchemaError("379 worst-case attempts do not fit the authorized study allocation")
    return config


def upper_cost(config):
    # Use the confirmed endpoint context bound, not a guessed tokenizer ratio.
    return ((Decimal(config["context_token_bound"]) * money(config["input_usd_per_million"])
             + Decimal(config["output_reservation_tokens"]) * money(config["output_usd_per_million"]))
            / Decimal(1_000_000) + money(config["request_usd"]))


def budget_configuration_hash(config):
    # A genuine prompt/interface correction may change code/prompts, not reset the
    # financial ledger. Pricing/model/cap changes require explicit reconciliation.
    fields = ("model", "provider_slug", "max_tokens", "output_reservation_tokens", "context_token_bound",
              "input_usd_per_million", "output_usd_per_million", "request_usd", "quota_usd")
    return digest({name: config[name] for name in fields}, "wgp-live-budget-config-v1")


def payload_for(request, config):
    validate_configuration(config)
    body = {"model": config["model"], "messages": [
        {"role": "system", "content": request["system"]},
        {"role": "user", "content": request["user"]}],
        "temperature": config["temperature"], "top_p": config["top_p"],
        "max_tokens": config["max_tokens"], "stream": False,
        "reasoning": {"effort": config["reasoning_effort"], "exclude": True},
        "provider": {"only": [config["provider_slug"]], "allow_fallbacks": False,
                     "require_parameters": True,
                     "data_collection": config["data_collection"],
                     "max_price": {"prompt": float(money(config["input_usd_per_million"])),
                                   "completion": float(money(config["output_usd_per_million"])),
                                   "request": float(money(config["request_usd"]))}},
        "plugins": []}
    if len(canonical(body).encode("utf-8")) > config["max_request_bytes"]:
        raise SchemaError("request exceeds frozen byte cap; do not send")
    return body


def visible_response(value):
    """Discard reasoning-text fields; retain visible answers and token accounting."""
    if type(value) is dict:
        return {key: visible_response(item) for key, item in value.items()
                if key not in ("reasoning", "reasoning_details")}
    if type(value) is list:
        return [visible_response(item) for item in value]
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class OpenRouterHTTP:
    kind = "official_openrouter_http"

    def __init__(self, api_key, timeout_seconds):
        if type(api_key) is not str or not api_key.strip():
            raise SchemaError("authorized secret attachment is missing")
        self._key = api_key
        self.timeout = timeout_seconds
        self.opener = urllib.request.build_opener(NoRedirect())

    def send(self, body):
        started, clock = timestamp(), time.perf_counter()
        record = {"started_at": started, "finished_at": None, "latency_seconds": None,
                  "http_status": None, "headers": {}, "response": None,
                  "transport_error": None, "retryable_transport": False}
        request = urllib.request.Request(ENDPOINT, data=canonical(body).encode("utf-8"),
                                         method="POST", headers={"Content-Type": "application/json",
                                         "Authorization": "Bearer " + self._key})
        try:
            response = self.opener.open(request, timeout=self.timeout)
        except urllib.error.HTTPError as error:
            response = error
        except (TimeoutError, urllib.error.URLError) as error:
            reason = error.reason if isinstance(error, urllib.error.URLError) else error
            timed_out = isinstance(reason, TimeoutError)
            record.update(transport_error="timeout" if timed_out else "network_error",
                          retryable_transport=timed_out)
            response = None
        if response is not None:
            with response:
                record["http_status"] = response.status
                record["headers"] = {name: response.headers[name] for name in
                                     ("x-request-id", "x-openrouter-request-id", "retry-after")
                                     if response.headers.get(name) is not None}
                try:
                    raw = response.read(2_000_001)
                    if len(raw) > 2_000_000:
                        raise SchemaError("provider response exceeds 2 MB")
                    text = raw.decode("utf-8").replace(self._key, "[REDACTED_CREDENTIAL]")
                    record["response"] = visible_response(strict_json(text, max_bytes=2_000_000))
                except (UnicodeError, SchemaError):
                    record["transport_error"] = "invalid_provider_envelope"
                except TimeoutError:
                    record.update(transport_error="timeout", retryable_transport=True)
            if record["http_status"] in (429, 502, 503, 504):
                record["retryable_transport"] = True
        record["finished_at"] = timestamp()
        record["latency_seconds"] = time.perf_counter() - clock
        return record


def interpret_receipt(receipt, config):
    """This function is rerun by the live auditor; metadata is not accepted on trust."""
    response = receipt["response"]
    usage = {**UNKNOWN_USAGE}
    retryable = (receipt["transport_error"] == "timeout" or receipt["http_status"] in (429, 502, 503, 504))
    if type(receipt["retryable_transport"]) is not bool or receipt["retryable_transport"] != retryable:
        raise SchemaError("transport retry eligibility contradicts HTTP status/error")
    result = {"status": "transport_error", "text": None, "usage": usage,
              "provider_request_id": None, "finish_reason": None, "fatal": False,
              "retryable": retryable, "error": receipt["transport_error"]}
    if type(response) is dict and type(response.get("usage")) is dict:
        cost = response["usage"].get("cost")
        if cost is not None:
            try:
                usage["cost_usd"] = float(money(cost))
            except SchemaError:
                result.update(status="integrity_error", fatal=True, retryable=False, error="invalid billed cost")
                return result
    if receipt["transport_error"] is not None or receipt["http_status"] != 200:
        result["fatal"] = not result["retryable"]
        result["error"] = result["error"] or "HTTP " + str(receipt["http_status"])
        return result
    try:
        if type(response) is not dict or "error" in response:
            raise SchemaError("provider error or non-object envelope")
        if response.get("model") != config["model"] or response.get("provider") != config["provider_response_name"]:
            raise SchemaError("response model/provider differs from approved route")
        if type(response.get("id")) is not str or not response["id"].strip():
            raise SchemaError("response lacks acquisition ID")
        result["provider_request_id"] = response["id"]
        choices = response.get("choices")
        if type(choices) is not list or len(choices) != 1 or type(choices[0]) is not dict:
            raise SchemaError("expected exactly one provider choice")
        choice = choices[0]
        message = choice.get("message")
        if (type(message) is not dict or message.get("role") != "assistant"
                or message.get("tool_calls") or message.get("function_call")):
            raise SchemaError("unexpected provider assistant message")
        text = message.get("content")
        if text is not None and type(text) is not str:
            raise SchemaError("visible content is not a string")
        result.update(text=text, finish_reason=choice.get("finish_reason"), retryable=False)
        raw_usage = response.get("usage")
        if type(raw_usage) is not dict:
            raise SchemaError("response lacks token usage")
        for source, target in (("prompt_tokens", "input_tokens"), ("completion_tokens", "output_tokens")):
            value = raw_usage.get(source)
            if type(value) is not int or value < 0:
                raise SchemaError("invalid token usage")
            usage[target] = value
        if (usage["input_tokens"] > config["context_token_bound"]
                or usage["output_tokens"] > config["output_reservation_tokens"]):
            raise SchemaError("provider usage exceeds frozen token caps")
        if (type(raw_usage.get("total_tokens")) is not int
                or raw_usage["total_tokens"] != usage["input_tokens"] + usage["output_tokens"]):
            raise SchemaError("inconsistent total tokens")
        for source, detail, target, bound in (
                ("completion_tokens_details", "reasoning_tokens", "reasoning_tokens", usage["output_tokens"]),
                ("prompt_tokens_details", "cached_tokens", "cached_input_tokens", usage["input_tokens"])):
            details = raw_usage.get(source) or {}
            value = details.get(detail)
            if value is not None and (type(value) is not int or not 0 <= value <= bound):
                raise SchemaError("invalid reasoning/cache token usage")
            usage[target] = value
        if usage["cost_usd"] is not None and money(usage["cost_usd"]) > upper_cost(config):
            raise SchemaError("provider billed above reserved upper bound")
        if message.get("refusal") or choice.get("finish_reason") == "content_filter":
            result.update(status="refused", error="provider refusal")
        elif choice.get("finish_reason") == "length":
            result.update(status="truncated", error="completion token limit reached")
        elif choice.get("finish_reason") != "stop" or text is None:
            raise SchemaError("unsupported finish reason or absent visible answer")
        else:
            result.update(status="response", error=None)
    except (SchemaError, TypeError, AttributeError) as error:
        result.update(status="integrity_error", fatal=True, retryable=False, error=str(error))
    return result