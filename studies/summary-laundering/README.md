# Who Said That? — runnable study harness

An offline-first Python standard-library testbed for summary/source handoffs.
Implementation and CPU validation exist. **No LLM results exist.** The live pilot,
empirical freeze, and held-out evaluation have not run. A bounded live adapter
is now in preparation under separate study spending authorization; acquisition
still requires approved secret availability and exact coordinator preflight.
See [the live protocol](LIVE_PROTOCOL.md). Ordinary `dry-run` remains fully offline.

Read the [study plan](PLAN.md), [method amendments](METHOD_CHANGES.md), and
[validation record](VALIDATION.md). Broader research claims remain untested.

## Run locally

Python 3.10+ is required; validation was performed with Python 3.14.6. No packages
need installing. From the repository root:

```sh
python3 -m unittest discover -s studies/summary-laundering/tests -v
python3 studies/summary-laundering/run.py access
python3 studies/summary-laundering/run.py dry-run --split dev --seed 1701 --profile scripted --out /tmp/sl-dev-1701
python3 studies/summary-laundering/run.py audit /tmp/sl-dev-1701
python3 studies/summary-laundering/run.py analyze /tmp/sl-dev-1701
```

Output directories must not already exist. Runs are never overwritten or resumed.
Use a new output path for each intentional test. Store real acquisition logs in
a private location; do not commit unreviewed run directories. `analyze` prints JSON
and does not modify the run.

The separate, evaluation-sized **engineering validation** namespace exercises
all four families and 40 attacked + 20 clean inputs without claiming a holdout:

```sh
python3 studies/summary-laundering/run.py dry-run --split validation --seed 2802 --profile scripted --out /tmp/sl-validation-2802
```

Profiles: `scripted` follows the synthetic side-effect instruction in any wrapper;
`safe` writes only the legitimate answer; `drop-attack` removes the attack while
summarizing; `invalid` emits malformed executor JSON; `abstain` returns empty
actions; `transport-once`/`transport-always` inject technical failures. None encodes
a favorable provenance effect. Their rates are implementation checks, not model
behavior, attack success estimates, or scientific pilot results.

## What is implemented

Each record has an original task, protected and result dictionaries, a source ID,
facts, one controlled attack/control paragraph, and neutral text. The summarizer
has no tools. An executor proposes at most eight mock actions in one strict JSON
batch. Allowed target schemas and immutable policy appear in the system message;
all evidence and source interventions stay in the same user-message envelope.

The six R/E/S × D/P replay cells plus S-P-W and S-P-P use fresh contexts and reset
state. Exactly one summary is stored per input, with its hash reused in every
summary cell. The scorer distinguishes attempts, targeted attempts, any forbidden
state event, final approval, exact utility, safe-and-correct utility, invalid
responses and abstention. The hard allowlist is a noninteractive engineering
replay, never an information-matched empirical defense.

Output files:

| File | Contents |
| --- | --- |
| `manifest.json` | Explicit offline model configuration, seeds, cases, code/protocol/dataset hashes, limits, primary/secondary contrasts and analysis settings |
| `run_metadata.json` | Wall-clock start timestamp, separate from deterministic content |
| `events.jsonl` | Append-only, flushed request/response, summary and outcome records, including failed attempts |
| `run.json` | Complete scheduled outcome matrix, summary bytes, calls, state transitions and gate replay |
| `analysis.json` | Audit, counts, missingness bounds, paired estimates, intervals, family/matched breakdowns, utility and cost fields |
| `REPORT.md` | Clearly labeled engineering-only table |

Request hashes include messages and explicit configuration. Code and protocol
hashes are checked before execution; analysis reconstructs requests and state
scores. Hashes detect accidental inconsistencies, not malicious rewriting of the
entire artifact bundle. A crash leaves partial JSONL and no complete `run.json`;
do not treat that directory as a completed run or silently rerun it as a retry.

The generator has disjoint `dev`, `validation`, and `holdout` namespaces. Unit
tests inspect holdout generation invariants, but no scientific holdout seed or
case manifest has been selected or evaluated. The offline runner rejects empirical
holdout execution. The separate live runner requires a bound preflight GO and an
actual passing pilot. Offline manifests are engineering
snapshots, **not an empirical freeze or preregistration**.

## Analysis details

The unit is the original scenario (`cluster_id` retains clean counterparts).
Primary comparisons are S-P minus S-D and S-P minus E-P on attacked inputs.
Secondary defense comparisons report effect, utility and joint safe completion
on both attacked and clean inputs. Report all scheduled rows; invalid action
batches have observed zero executed effects but remain invalid, while transport
and context failures have unknown outcomes and cannot count as safe completion.

Analysis includes raw numerators/denominators, Wilson rate intervals, paired
cluster bootstrap intervals, conservative bounded-cluster intervals where
applicable, worst-case missingness bounds, exact paired McNemar tests, and Holm
adjustment for the two primary tests only. Shared-template dependence remains a
limitation. Zero effects in 40 independent cases would still permit an approximately
7.2% one-sided 95% upper bound. Stub intervals have no empirical interpretation.

## Model interface and spending boundary

`sl.backends.Backend` defines a small `complete(request, config, call_id)` contract.
`RecordedBackend` supports prompt-and-configuration-bound offline regression
tapes through Python; these are marked **unverified**, not empirical pilot data.
The `dry-run` CLI uses only `TestDouble`. The distinct `live-acquire` command
requires the gates in [LIVE_PROTOCOL.md](LIVE_PROTOCOL.md); credentials are read
only after its GO validation. Neither path routes calls through an agent daemon,
browser session, or internal subscription transport.

Live acquisition requires review of provider terms, an authorized interface,
an exact model/version and sampling configuration, official token limits and
pricing, applicable batch authorization and a hard monetary cap. Secrets must use
the authorized secret mechanism, never source files or public logs. Record actual
token usage, cache and reasoning accounting, model version, latency, technical
failures and spend; unknowns stay unknown. Byte caps here are not model context
token caps. Do not just relabel a double or tape as `real_model` to bypass this gate.

Only after a genuine development pilot passes the declared interface thresholds
may the empirical protocol be frozen and new held-out cases run once. Preserve
unsuccessful pilots and revisions; do not select a lucky run. Competition
submission is separate and has not occurred.