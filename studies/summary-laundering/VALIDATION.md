# Engineering validation

This file records software tests only. No LLM results or scientific holdout have
been produced. On 8 November 2026 UTC, **90 tests passed** with Python 3.14.6
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