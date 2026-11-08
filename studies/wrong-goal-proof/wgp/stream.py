"""Bounded OpenRouter SSE assembly, with visible-only records and no SDK retries."""

import hashlib
import signal
import threading
from contextlib import contextmanager

from .logic import SchemaError, canonical, keys, strict_json


MAX_WIRE_BYTES = 8_000_000


@contextmanager
def wall_timeout(seconds):
    """A hard wall timer in the single-threaded POSIX acquisition process."""
    if threading.current_thread() is not threading.main_thread():
        raise SchemaError("acquisition requires the main thread for a bounded HTTP wall timer")
    if signal.getitimer(signal.ITIMER_REAL) != (0.0, 0.0):
        raise SchemaError("an existing process alarm would conflict with the HTTP deadline")
    previous = signal.getsignal(signal.SIGALRM)
    def expired(signum, frame):
        raise TimeoutError("bounded HTTP wall deadline")
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def assemble(chunks, done):
    """Rerunnable visible SSE audit: identity, one answer, usage, finish, DONE."""
    if type(chunks) is not list or done is not True:
        raise SchemaError("incomplete SSE stream: final DONE required")
    identity, contents, usage, finish, role, refusals = {}, [], None, None, None, []
    usage_index, finish_index = -1, -1
    for index, chunk in enumerate(chunks):
        if type(chunk) is not dict or chunk.get("error") is not None:
            raise SchemaError("provider error or non-object SSE event")
        for name in ("id", "model", "provider"):
            if name in chunk and chunk[name] is not None:
                value = chunk[name]
                if type(value) is not str or not value.strip():
                    raise SchemaError("invalid SSE provider identity")
                if name in identity and identity[name] != value:
                    raise SchemaError("provider identity changed within SSE stream")
                identity[name] = value
        if chunk.get("usage") is not None:
            if type(chunk["usage"]) is not dict or usage is not None:
                raise SchemaError("duplicate or invalid final SSE usage")
            usage = chunk["usage"]
            usage_index = index
        choices = chunk.get("choices")
        if type(choices) is not list or len(choices) > 1:
            raise SchemaError("expected zero or one SSE choice")
        if not choices:
            continue
        choice = choices[0]
        if type(choice) is not dict or type(choice.get("index")) is not int or choice["index"] != 0:
            raise SchemaError("invalid SSE choice index")
        delta = choice.get("delta")
        if type(delta) is not dict or delta.get("tool_calls") or delta.get("function_call"):
            raise SchemaError("invalid SSE delta or unexpected tool call")
        if delta.get("role") is not None:
            if delta["role"] != "assistant":
                raise SchemaError("unexpected SSE role")
            role = "assistant"
        content = delta.get("content")
        if delta.get("refusal") is not None:
            if type(delta["refusal"]) is not str:
                raise SchemaError("invalid SSE refusal")
            refusals.append(delta["refusal"])
        if content is not None:
            if type(content) is not str or (finish is not None and content):
                raise SchemaError("invalid content or content after SSE finish")
            contents.append(content)
        if choice.get("finish_reason") is not None:
            if finish is not None or type(choice["finish_reason"]) is not str:
                raise SchemaError("duplicate or invalid SSE finish")
            finish = choice["finish_reason"]
            finish_index = index
    if (set(identity) != {"id", "model", "provider"} or usage is None or finish is None
            or role != "assistant" or usage_index < finish_index):
        raise SchemaError("SSE lacks complete provider identity, assistant role, usage or finish")
    return {**identity, "choices": [{"index": 0, "finish_reason": finish,
            "message": {"role": "assistant", "content": "".join(contents), "refusal": "".join(refusals) or None}}], "usage": usage}


def read_sse(response, redact, visible, record):
    """Preserve every parsed visible event; never persist reasoning-text fields."""
    trace = {"chunks": [], "done": False, "wire_bytes": 0, "wire_sha256": None}
    record["stream"] = trace
    hasher, event_lines = hashlib.sha256(), []

    def dispatch():
        if not event_lines:
            return
        text = "\n".join(event_lines)
        event_lines.clear()
        if text == "[DONE]":
            trace["done"] = True
            return
        if trace["done"]:
            raise SchemaError("SSE data after DONE")
        trace["chunks"].append(visible(strict_json(redact(text), max_bytes=MAX_WIRE_BYTES)))

    try:
        while True:
            raw = response.readline(MAX_WIRE_BYTES + 1)
            if not raw:
                dispatch()
                break
            trace["wire_bytes"] += len(raw)
            hasher.update(raw)
            if trace["wire_bytes"] > MAX_WIRE_BYTES:
                raise SchemaError("SSE exceeds the frozen wire-byte ceiling")
            line = raw.decode("utf-8").rstrip("\r\n")
            if not line:
                dispatch()
                if trace["done"]:
                    break
            elif line.startswith("data:"):
                data = line[5:]
                event_lines.append(data[1:] if data.startswith(" ") else data)
            elif line.startswith(":") or line.startswith(("event:", "id:", "retry:")):
                continue
            else:
                raise SchemaError("unsupported SSE field")
        return assemble(trace["chunks"], trace["done"])
    finally:
        trace["wire_sha256"] = hasher.hexdigest()


def audit_stream(trace, response):
    keys(trace, ("chunks", "done", "wire_bytes", "wire_sha256"))
    if (type(trace["wire_bytes"]) is not int or not 0 < trace["wire_bytes"] <= MAX_WIRE_BYTES
            or type(trace["wire_sha256"]) is not str or len(trace["wire_sha256"]) != 64):
        raise SchemaError("invalid bounded SSE wire record")
    assembled = assemble(trace["chunks"], trace["done"])
    if canonical(assembled) != canonical(response):
        raise SchemaError("visible response differs from the recorded SSE events")
    return assembled