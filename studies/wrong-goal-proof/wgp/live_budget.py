"""One-study durable budget ledger. Unknown charges never become zero.

The lock covers reservation, HTTP acquisition, and settlement. An abandoned
reservation remains fully committed after restart. No SDK or hidden retries.
"""

import fcntl
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .logic import SchemaError, canonical, digest, keys, strict_json
from .pipeline import timestamp


class BudgetStop(RuntimeError):
    pass


def money(value):
    if type(value) not in (str, int, float, Decimal):
        raise SchemaError("cost must be a decimal string or numeric amount")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise SchemaError("invalid decimal cost") from exc
    if not result.is_finite() or result < 0:
        raise SchemaError("cost must be finite and nonnegative")
    return result


def ledger_state(events, configuration_hash, quota="20"):
    """Replay a hash-chained ledger; validate all limits, not only its last row."""
    reservations, settlements, retries = {}, {}, 0
    stages = {"pilot-v1": set(), "pilot-v2": set(), "main": set()}
    previous = None
    for sequence, event in enumerate(events):
        keys(event, ("sequence", "previous_hash", "configuration_hash", "timestamp",
                     "action", "data", "event_hash"))
        core = {k: v for k, v in event.items() if k != "event_hash"}
        if (type(event["sequence"]) is not int or event["sequence"] != sequence
                or event["previous_hash"] != previous
                or event["configuration_hash"] != configuration_hash
                or event["event_hash"] != digest(core, "wgp-budget-event-v1")):
            raise SchemaError("budget journal hash/configuration/order mismatch")
        previous = event["event_hash"]
        data = event["data"]
        if event["action"] == "reserve":
            keys(data, ("attempt_id", "logical_id", "stage", "request_hash", "reserve_usd", "retry_of"))
            aid, lid, stage = data["attempt_id"], data["logical_id"], data["stage"]
            if any(s["confirmed_charge_usd"] is not None and money(s["confirmed_charge_usd"]) > money(reservations[a]["reserve_usd"])
                   for a, s in settlements.items()):
                raise SchemaError("reservation after a pricing overrun is forbidden")
            if (type(aid) is not str or aid in reservations or type(lid) is not str
                    or stage not in stages or type(data["request_hash"]) is not str):
                raise SchemaError("invalid or duplicate budget reservation")
            prior = [r for r in reservations.values() if r["logical_id"] == lid and r["stage"] == stage]
            if data["retry_of"] is None:
                if prior:
                    raise SchemaError("logical request already reserved; no silent resume/resample")
                stages[stage].add(lid)
                limit = 260 if stage == "main" else 52
                if len(stages[stage]) > limit:
                    raise SchemaError("stage logical-call limit exceeded")
            else:
                parent = reservations.get(data["retry_of"])
                settled = settlements.get(data["retry_of"])
                if (len(prior) != 1 or parent is None or settled is None
                        or not settled["retryable"] or parent["request_hash"] != data["request_hash"]
                        or parent["logical_id"] != lid or parent["stage"] != stage):
                    raise SchemaError("retry is not one identical technical retry")
                retries += 1
            if retries > 15 or len(reservations) >= 379:
                raise SchemaError("total attempt/retry limit exceeded")
            reserve = money(data["reserve_usd"])
            committed = sum((money(settlements[a]["confirmed_charge_usd"])
                             if a in settlements and settlements[a]["confirmed_charge_usd"] is not None
                             else money(r["reserve_usd"])) for a, r in reservations.items())
            if committed + reserve > money(quota):
                raise SchemaError("reservation exceeds the assigned USD20 quota")
            reservations[aid] = data
        elif event["action"] == "settle":
            keys(data, ("attempt_id", "confirmed_charge_usd", "retryable", "receipt_hash"))
            aid = data["attempt_id"]
            if aid not in reservations or aid in settlements or type(data["retryable"]) is not bool:
                raise SchemaError("invalid or repeated settlement")
            if data["confirmed_charge_usd"] is not None:
                money(data["confirmed_charge_usd"])
            if type(data["receipt_hash"]) is not str:
                raise SchemaError("settlement needs an acquisition receipt hash")
            settlements[aid] = data
        else:
            raise SchemaError("unknown budget journal action")
    committed = sum((money(settlements[a]["confirmed_charge_usd"])
                     if a in settlements and settlements[a]["confirmed_charge_usd"] is not None
                     else money(r["reserve_usd"])) for a, r in reservations.items())
    known = sum((money(s["confirmed_charge_usd"]) for s in settlements.values() if s["confirmed_charge_usd"] is not None), Decimal(0))
    unknown = sum(a not in settlements or settlements[a]["confirmed_charge_usd"] is None for a in reservations)
    overrun = any(s["confirmed_charge_usd"] is not None and money(s["confirmed_charge_usd"]) > money(reservations[a]["reserve_usd"])
                  for a, s in settlements.items())
    return {"reservations": reservations, "settlements": settlements, "retries": retries,
            "attempts": len(reservations), "committed_usd": str(committed),
            "settled_conservative_usd": str(known), "unknown_charges": unknown,
            "pricing_overrun": overrun, "last_hash": previous,
            "logical_counts": {stage: len(ids) for stage, ids in stages.items()}}


class BudgetLedger:
    def __init__(self, path, configuration_hash, quota="20"):
        if money(quota) != Decimal("20"):
            raise SchemaError("this study is authorized for exactly a USD20 maximum allocation")
        self.path = Path(path)
        self.configuration_hash, self.quota = configuration_hash, quota
        self.lock = None
        self.events = []

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = os.open(str(self.path) + ".lock", os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if self.path.exists():
                raw = self.path.read_text(encoding="utf-8")
                if raw and not raw.endswith("\n"):
                    raise SchemaError("torn budget journal: acquisition must stop")
                self.events = [strict_json(line) for line in raw.splitlines()]
            ledger_state(self.events, self.configuration_hash, self.quota)
        except BaseException:
            os.close(self.lock)
            self.lock = None
            raise
        return self

    def __exit__(self, *args):
        if self.lock is not None:
            fcntl.flock(self.lock, fcntl.LOCK_UN)
            os.close(self.lock)
            self.lock = None

    def state(self):
        return ledger_state(self.events, self.configuration_hash, self.quota)

    def append(self, action, data):
        if self.lock is None:
            raise RuntimeError("budget operations require the exclusive study lock")
        event = {"sequence": len(self.events), "previous_hash": self.state()["last_hash"],
                 "configuration_hash": self.configuration_hash, "timestamp": timestamp(),
                 "action": action, "data": data}
        event["event_hash"] = digest(event, "wgp-budget-event-v1")
        ledger_state(self.events + [event], self.configuration_hash, self.quota)
        descriptor = os.open(self.path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
            stream.write(canonical(event) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.events.append(event)
        return event

    def reserve(self, logical_id, stage, request_hash, upper_cost, retry_of=None):
        state = self.state()
        if state["pricing_overrun"]:
            raise BudgetStop("provider charge exceeded reservation; stop pending reconciliation")
        attempt_id = f"attempt-{state['attempts'] + 1:04d}"
        data = {"attempt_id": attempt_id, "logical_id": logical_id, "stage": stage,
                "request_hash": request_hash, "reserve_usd": str(money(upper_cost)), "retry_of": retry_of}
        try:
            self.append("reserve", data)
        except SchemaError as exc:
            raise BudgetStop(str(exc)) from exc
        return attempt_id

    def settle(self, attempt_id, confirmed_charge_usd, retryable, receipt):
        return self.append("settle", {"attempt_id": attempt_id,
                           "confirmed_charge_usd": None if confirmed_charge_usd is None else str(money(confirmed_charge_usd)),
                           "retryable": retryable, "receipt_hash": digest(receipt, "wgp-receipt-v1")})