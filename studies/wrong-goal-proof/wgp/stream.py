"""Bounded OpenRouter SSE assembly, with visible-only records and no SDK retries."""

import hashlib
import signal
import threading
from contextlib import contextmanager

from .logic import SchemaError, canonical, keys, strict_json
from .pacing import safe_error_envelope


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
    usage_index, finish_index, native_finish = -1, -1, None
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
            if type(delta["refusal"]) is not str or (finish is not None and delta["refusal"]):
                raise SchemaError("invalid SSE refusal")
            refusals.append(delta["refusal"])
        if content is not None:
            if type(content) is not str or (finish is not None and content):
                raise SchemaError("invalid content or content after SSE finish")
            contents.append(content)
        if choice.get("finish_reason") is not None:
            terminal = choice["finish_reason"]
            if type(terminal) is not str or (finish is not None and terminal != finish):
                raise SchemaError("conflicting or invalid SSE finish")
            if finish is not None:
                # The observed OpenRouter footer repeats the terminal choice
                # with final usage. Accept only that final, empty, idempotent
                # receipt, never a second answer or a continuing stream.
                if (index != len(chunks) - 1 or chunk.get("usage") is None
                        or choice.get("native_finish_reason") != native_finish
                        or set(delta) - {"role", "content", "refusal"}
                        or content or delta.get("refusal")):
                    raise SchemaError("non-idempotent duplicate SSE terminal finish")
            else:
                finish, finish_index, native_finish = terminal, index, choice.get("native_finish_reason")
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
        raw_chunk = strict_json(redact(text), max_bytes=MAX_WIRE_BYTES)
        chunk = visible(raw_chunk)
        if type(raw_chunk) is dict and raw_chunk.get("error") is not None:
            trace["chunks"].append(safe_error_envelope(raw_chunk))
            return
        # Preserve only the fact that hidden fields existed, never their text.
        # This lets the repeatable audit reject hidden continuation in a footer.
        if type(raw_chunk) is dict and type(raw_chunk.get("choices")) is list:
            for raw_choice, choice in zip(raw_chunk["choices"], chunk["choices"]):
                raw_delta = raw_choice.get("delta") if type(raw_choice) is dict else None
                if (type(raw_delta) is dict and any(raw_delta.get(k) is not None
                        for k in ("reasoning", "reasoning_details", "reasoning_content"))):
                    choice["delta"]["reasoning_fields_removed"] = True
        trace["chunks"].append(chunk)

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