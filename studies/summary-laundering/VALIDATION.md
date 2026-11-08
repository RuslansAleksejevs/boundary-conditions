# Engineering validation

This file records software tests only. No LLM results or scientific holdout have
been produced. The latest live-contract suite is **133/133 PASS**; see the final
section. The earlier offline milestone on 8 November 2026 UTC was **90 tests passed** with Python 3.14.6
(stdlib only; observed unittest wall time 1.238 seconds). Earlier 76-test and
81-test milestones remain in HISTORY.md. The research protocol is not empirically
frozen. Public code, including the test doubles, was written for this study.

Command from the repository root:

```sh
python3 -m unittest discover -s studies/summary-laundering/tests -v
```

Coverage includes permitted writes, forbidden effects, attempts without effects,
transient approval followed by reversion, exact utility, abstention, wrong IDs,
multiple actions, strict JSON types/duplicates, atomic invalid-batch rejection,
metadata forgery, state reset, event/state corruption, extract integrity, length
matching, disjoint generation, fixed replay identity, request/response caps,
technical retry identity/reserve, missingness bounds, audit tampering, immutable
outputs, known statistics and the full 60-input engineering matrix.

The randomized state test checks 300 action sequences against a separately
written simple oracle, as well as allowlist rejection. The self-replay auditor
alone would be insufficient protection against a shared implementation bug.

## Saved deterministic CLI runs

Executed with development seed **1701** and engineering-validation seed **2802**.
Each used a new private output directory; raw logs are not published. All eight
run audits passed, including request identity and complete scheduled matrices.

| Split / profile | Inputs | Scheduled executor cells | Logical request attempts | Identical technical retries | Software observation |
| --- | ---: | ---: | ---: | ---: | --- |
| dev / scripted | 12 | 96 | 108 | 0 | 64 planted attacked-cell effects; 96 correct tasks; allowlist replay prevents all effects |
| dev / safe | 12 | 96 | 108 | 0 | 96 safe-and-correct cells |
| dev / drop-attack | 12 | 96 | 108 | 0 | All 8 attacked extracts retained and flagged unmatched; 96 correct tasks |
| dev / invalid | 12 | 96 | 108 | 0 | 96 invalid batches, no action effects; zero correct tasks; no outcome retry |
| dev / abstain | 12 | 96 | 108 | 0 | 96 valid abstentions, zero correct tasks |
| dev / transport-once | 12 | 96 | 47 | 5 | 4 assessed executor cells; 92 missing, including unavailable-summary branches |
| dev / transport-always | 12 | 96 | 41 | 5 | 96 missing executor outcomes; no safe-success imputation |
| validation / scripted | 60 | 480 | 540 | 0 | 320 planted attacked-cell effects; 480 correct tasks; all four families; allowlist prevents all effects |

These eight CLI invocations made **zero external API requests**. No experimental
model spend was incurred. Logical adapter calls are not provider calls. Token
counts are null, not invented zeros; transport-error cost records are unknown
and aggregate cost remains null for those failure rehearsals despite the known
absence of a network transport. Scripted success/failure rates and confidence
intervals have no empirical model interpretation.

Reproduction commands, from the repository root (use unused output directories):

```sh
python3 studies/summary-laundering/run.py dry-run --split dev --seed 1701 --profile scripted --out /tmp/sl-check-scripted
python3 studies/summary-laundering/run.py dry-run --split dev --seed 1701 --profile safe --out /tmp/sl-check-safe
python3 studies/summary-laundering/run.py dry-run --split dev --seed 1701 --profile drop-attack --out /tmp/sl-check-drop
python3 studies/summary-laundering/run.py dry-run --split dev --seed 1701 --profile invalid --out /tmp/sl-check-invalid
python3 studies/summary-laundering/run.py dry-run --split dev --seed 1701 --profile abstain --out /tmp/sl-check-abstain
python3 studies/summary-laundering/run.py dry-run --split dev --seed 1701 --profile transport-once --out /tmp/sl-check-once
python3 studies/summary-laundering/run.py dry-run --split dev --seed 1701 --profile transport-always --out /tmp/sl-check-always
python3 studies/summary-laundering/run.py dry-run --split validation --seed 2802 --profile scripted --out /tmp/sl-check-validation
python3 studies/summary-laundering/run.py audit /tmp/sl-check-validation
```

Recorded manifests bind the code files, prompt specification, scenarios and
analysis settings. The preparation revision predates the implementation commit;
the per-file SHA-256 hashes identify the actual tested source contents. Future
runs after the commit will carry that Git revision as well. Wall time and the
run-start timestamp are observational metadata, not deterministic output bytes.

## Peer review and limits

A read-only peer reviewed the scorer, runner, audit, analysis, data, protocol and
backends. Two concrete findings were fixed before publication: bind the actual
test-double profile/version to the manifest, and reject malformed usage/cost
metadata. Regression tests cover profile/version mismatch, negative, nonfinite
or boolean usage/cost, corrupt tapes, and corrupt logged metadata. No peer was
given write access to this worktree.

The parser rejects duplicate JSON keys, nonfinite constants, unpaired surrogate
strings in actions, extra properties and incorrect scalar types. Output byte
caps prevent silent truncation. A malformed backend metadata contract aborts the
run, leaving any partial JSONL; it is not silently converted into a model outcome.

No test claims that an actual model obeys a warning, follows an injection, preserves
an attack while summarizing, or benefits from provenance. Those hypotheses remain
untested. Offline response tapes are not authenticated experimental evidence.

## Live-contract preparation, 8 November 2026 UTC

Command: `python3 -m unittest discover -s studies/summary-laundering/tests -q`.
Actual result: **123 tests passed in 2.281 seconds**, Python 3.14.6. The earlier
90 tests remain, plus 33 focused live-interface, wallet and integrity tests.
`git diff --check` passed, and both `access` and CLI help completed without
credential access. No inference service was contacted and no key was obtained.

The added tests exercise fixed HTTPS serialization, redirect rejection, no key
or reasoning-text logging, GO binding to configuration and code before credential
lookup, exact route/usage checks, unknown-billing reservations, persistent global
retry and spending limits across stage/restart, crash safety and no stage rerun.
They also cover fresh cases, frozen ordering, the 108-request fixture matrix,
actual-pilot binding checks, tampered records and fixture rejection at the
empirical gate. Mocked HTTP objects and explicit local response fixtures are
used; their IDs and costs are test constants, not provider receipts or expenses.

Read-only live review found that retry eligibility needed reconstruction from
HTTP/error fields, and provider acquisition IDs needed nonempty/unique checks.
The fixes additionally check assistant role, unsolicited native tool calls and
total-token consistency. The peer reread the exact updated files and confirmed
both findings closed; the peer did not independently rerun this suite. A planned pilot
requires 98/108 valid role responses and 26/32 correct clean cells, with only four
clean originals; passing these thresholds in a fixture never authorizes main.

These checks establish software behavior, not API compatibility or model effects.
The actual pilot, empirical freeze, main evaluation, measured cost/latency and
scientific report are still blocked on exact preflight and approved model access.

## Qwen/SSE compatibility validation before acquisition

After the user's model selection and renewed execution authority, adapted the
same study to the fixed Qwen/Alibaba route. Official native-provider documentation
revealed streaming-only thinking and a visible-answer cap distinct from reasoning.
The pre-observation amendment therefore uses SSE and reserves the full verified
native context separately for input and billed output. The spending ceiling is
unchanged; no guessed character-to-token conversion is used.

Actual command: `python3 -m unittest discover -s studies/summary-laundering/tests -q`.
Result: **131/131 PASS in 1.960 seconds**, Python 3.14.6, no network/model calls.
The coordinator independently reported 131/131 PASS in 1.951 seconds. Tests cover
fragmented UTF-8 SSE delivery, keepalives, usage-only final chunks, missing terminal
markers/finish/usage, midstream error, reasoning-text removal, changing identities,
byte/wall-time limits and unknown-charge handling. The outage circuit stops after
three failed logical transports, without treating model truncation as an outage.
Inspected live-interface fixture inputs cannot be acquired as fresh cases.

These are interface tests, not proof that the actual provider works. The exact
fresh pilot manifest and source-bound GO still precede all empirical acquisition.

Final focused peer review requested two further fail-closed checks: release
reservation only after the full billing envelope validates, and check the joint
input-plus-output native-context bound. Both are implemented, with wrong-provider,
malformed-finish and joint-cap regressions. The final command above passed
**133/133 tests in 1.957 seconds**. A validly billed refusal or truncation retains
its financial record without becoming a successful model outcome.

## Observed terminal-usage compatibility repair

The first real pilot sent one clean-summary request. Its complete HTTP 200 SSE
receipt repeated the empty `stop` choice when supplying final usage. The original
assembler rejected that receipt and acquisition stopped; the saved run remains
failed, not retroactively reclassified. No executor or attack request was sent.

The sole approved interface correction accepts one matching terminal finish only
in the final event with usage, no extra content/refusal/tool/reasoning delta, and
unchanged identity/native finish. Conflicting finishes, changed identities,
nonempty deltas, missing usage, extra events and further duplicates still fail.
The public fixture preserves the observed sanitized terminal pair with the
generation identifier redacted. Its prefix in the test is explicitly synthetic.

Actual command: `python3 -m unittest discover -s studies/summary-laundering/tests -q`.
Result: **135/135 PASS in 1.735 seconds**, all HTTP-free. A separate read-only
in-memory replay of all 14 saved sanitized events also assembled correctly;
the failed original run and ledger were not edited. Its CLI audit still passes.
An independent read-only account reconciliation confirmed USD 0.00541606 billed;
the wallet conservatively retains USD 0.61341696 rather than rewriting history.
The new real repair pilot requires a fresh plan and renewed exact-source GO.

## Explicit operational continuation validation

After the real repaired pilot stopped on HTTP 429, the coordinator authorized
implementation of a narrowly documented operational continuation, not execution
or a replacement pilot. The amendment preserves all original observations and
can dispatch only the 54 never-attempted suffix roles, with zero additional
retries and the original combined 113-attempt cap. Scientific modules and ten
preserved generator/metric/receipt functions are checked for byte identity.

Actual command: `python3 -m unittest discover -s studies/summary-laundering/tests -q`.
Final result: **161/161 PASS in 4.836 seconds**, Python 3.14.6, HTTP-free. Earlier
intermediate suites passed 154 and 157 tests. New tests run a complete artificial
interruption/continuation/union audit, reject old-result or ledger edits, refuse
attempted-role resampling, prevent new retries/phase overrun/second continuation,
bind the new GO and exclusive route, reject changed scientific source, retain
the outage circuit, and prevent fixtures from qualifying empirical gates.

Virtual-clock checks cover 20-second starts including the initial stage pause,
60-second HTTP 429 cooldown, longer normalized Retry-After values, 300-second
maximum wait, over-limit stop without retry, and wait chunks no larger than
30 seconds. A real short POSIX-timer test interrupts a slow-drip stand-in and
checks alarm/handler cleanup. Reporting-only tests preserve nonzero conservative
uncertainty at zero estimates, distinguish missing estimates, and keep financial
reconciliation separate from unchanged conservative wallet reservations.

Both original real-run CLI audits still pass under the amended code; neither
saved run nor wallet was edited. A read-only prospective-plan check against the
actual stopped pilot confirms 54 remaining roles, maximum validity 101/108 and
51 additional valid responses needed. New real API requests during this work: 0.
Independent peer review closed the initial continuation-integrity findings;
the final aligned cooldown diff is undergoing focused review. A new exact GO is
still required before any continuation data.