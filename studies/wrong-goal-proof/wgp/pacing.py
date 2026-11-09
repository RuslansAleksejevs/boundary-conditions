"""Prospective transport pacing; no retries, networking or credentials here."""

import math
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from .logic import SchemaError


PACING_POLICY = {
    "version": 1,
    "minimum_attempt_start_interval_seconds": 20,
    "minimum_429_cooldown_seconds": 60,
    "maximum_accepted_retry_after_seconds": 300,
    "maximum_sleep_chunk_seconds": 30,
    "retry_after_over_limit": "stop_without_retry",
    "missing_or_invalid_retry_after": "use_minimum_429_cooldown",
    "attempts_and_retry_limits_unchanged": True,
}


def safe_retry_after(value, now=None):
    """Return only a canonical nonnegative delay; never retain arbitrary headers.

    HTTP dates are converted at receipt time and rounded up. Starting a cooldown
    after the response body has finished can only make that date-based wait later.
    """
    if type(value) is not str or len(value) > 128:
        return None
    value = value.strip()
    if value.isascii() and value.isdigit():
        return str(int(value))
    try:
        date = parsedate_to_datetime(value)
        if date.tzinfo is None:
            return None
        now = now or datetime.now(timezone.utc)
        return str(max(0, math.ceil((date - now).total_seconds())))
    except (TypeError, ValueError, OverflowError):
        return None


def cooldown(headers):
    value = headers.get("retry-after")
    # Persisted headers contain only normalized decimal seconds, not raw text.
    delay = int(value) if type(value) is str and len(value) <= 128 and value.isascii() and value.isdigit() else 60
    return None if delay > 300 else max(60, delay)


def safe_error_envelope(body):
    """Allowlisted error diagnostics only; never retain a raw provider error."""
    error = body.get("error") if type(body) is dict else None
    error = error if type(error) is dict else {}
    result = {}
    code = error.get("code")
    if type(code) is int or (type(code) is str and code in {
            "rate_limit_exceeded", "rate_limit", "too_many_requests", "429",
            "insufficient_quota", "provider_error", "overloaded"}):
        result["code"] = code
    metadata = error.get("metadata")
    metadata = metadata if type(metadata) is dict else {}
    for name in ("limit_source", "reason"):
        value = error.get(name, metadata.get(name))
        if type(value) is str and value in {
                "provider", "openrouter", "account", "model", "api_key", "organization",
                "requests", "tokens", "rpm", "tpm", "rate_limit_exceeded",
                "too_many_requests", "insufficient_quota", "capacity", "overloaded"}:
            result[name] = value
    return {"error": result}


class Pacer:
    def __init__(self, clock=None, sleep=None):
        self.clock, self.sleep = clock or time.monotonic, sleep or time.sleep
        self.next_start = self.clock()
        self.blocked = False

    def wait_before_start(self):
        if self.blocked:
            raise SchemaError("Retry-After exceeds 300 seconds; acquisition must stop")
        while (remaining := self.next_start - self.clock()) > 0:
            self.sleep(min(30, remaining))
        started = self.clock()
        self.next_start = started + 20
        return started

    def after_response(self, status, headers):
        if status == 429:
            delay = cooldown(headers)
            if delay is None:
                self.blocked = True
            else:
                self.next_start = max(self.next_start, self.clock() + delay)

    def after_prior_stage(self, receipt):
        # A new process cannot recover its predecessor's monotonic origin.
        # Waiting at least 20s from now conservatively covers the prior start.
        self.next_start = max(self.next_start, self.clock() + 20)
        self.after_response(receipt["http_status"], receipt["headers"])