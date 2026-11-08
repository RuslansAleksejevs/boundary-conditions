# Study history

Append-only engineering and research record. Plans and test doubles are not model
observations. Dates are UTC unless explicitly stated otherwise.

## 2026-11-08 — Initial implementation and ground-truth validation

PROJECT_REPORTED; sources: code in `wgp/`, tests in `tests/`, and local commands.
Implemented strict Boolean AST and controlled rendering, scalar exhaustive solver,
independent bit-vector verifier, separate open-function and closed-claim checks,
all four injected-fault and all four equivalent-rewrite families, a 20-case
development set and 100-case engineering holdout, semantic/skeleton split checks,
natural/replay pipelines, offline adapters, manifests, freeze rehearsal, and analysis.

The first 56-test run found one failure: Python 3.14 accepted JSON nesting deeper
than the test expected. Added an explicit nesting bound instead of relying on
interpreter recursion behavior. The subsequent expanded 97-test suite passed in
5.378 seconds. It includes 2,400 random ASTs, all 256 three-atom Boolean functions,
600 randomized solver/checker contracts, and malformed certificate checks.

Read-only peer review confirmed the scope distinctions and proposed stronger
response/status consistency checks. Implemented those checks, incremental event
logging, full-schedule paired missingness bounds, and additional regression tests.
The final pass and measured rehearsal outputs will be recorded separately.

No real model experiment or external experimental spending occurred. Local
test-double behavior is explicitly synthetic. No competition submission occurred.

## 2026-11-08 — Expanded integrity suite passes

PROJECT_REPORTED; command:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=studies/wrong-goal-proof python3 -m unittest discover -s studies/wrong-goal-proof/tests -q`.
104 tests passed in 4.556 seconds on Python 3.14.6. Added standalone false-guarantee
packet export/verification and tests for certificate, witness, hash, claim and
duplicate-case corruption. Request/response/status consistency, Boolean score
types, invocation flags, latency, and incremental journals are now checked.
Documented engineering-versus-empirical holdout, offline chronology limitations,
the 12-original-clean-case pilot denominator, and missingness bounds.
No real pilot or confirmatory LLM holdout has run or been frozen.

## 2026-11-08 — Pre-publication implementation check

The same unittest command passed 105 tests in 5.611 seconds on Python 3.14.6.
The additional regression verifies that invalid Unicode is recorded as a schema
error rather than an unhandled exception. Normalized final newlines, reviewed
the staged study-only paths, and scanned for personal paths, credentials and
private coordination identifiers; no matches were found. No experimental model
calls or spending occurred. The implementation is ready for synthetic rehearsals.

## 2026-11-08 — Six audited synthetic rehearsals

Implementation commit `c15e8401a9c41f4bf73deee3a02bdbf82394cc47`; Python 3.14.6;
seed 6006. Saved perfect and local-only development/freeze/engineering-holdout
chains, plus abstaining and malformed development runs. Total: 728 local adapter
invocations and 616 reviewer outcomes across six runs, zero experimental model
calls, zero new external experimental cost. The two failed pilots were retained;
CLI freeze returned exit 2 and did not create their freeze files.

On the 40 planted engineering originals, perfect/local-only doubles produced
0/40 and 40/40 false SAFE in each of B/N/S, respectively. Both had natural utility
40/40 and equivalent-control utility 20/20 in each arm. Both scope contrasts are
zero by the scripted behavior, not empirical null results. Standalone evidence
verification confirmed all 40 originals and 120 scripted false guarantees.

Prepared reviewed aggregate JSON and a complete synthetic counterexample packet;
run/profile hashes are recorded in results/RECORD.json. All actual counts, commands,
uncertainty caveats, and limits are in VALIDATION.md. The engineering holdout is
explicitly not an untouched or preregistered confirmatory LLM evaluation.

All six saved runs were re-audited before publication. Recomputed analysis matched
each public aggregate exactly; the exported packet matched the audited local run,
and every file hash in results/RECORD.json matched. Repository diff checks passed.

## 2026-11-08 — Study branch published for coordinator review

Pushed the study-only implementation and reviewed synthetic results to
`study/wrong-goal-proof`, then opened
https://github.com/RuslansAleksejevs/boundary-conditions/pull/2 into `main`.
Implementation commit: `c15e8401a9c41f4bf73deee3a02bdbf82394cc47`;
rehearsal/results commit: `b851d515fbcd43f5ab1065412c7c3f2ff6ce85bf`.
Fetched the current upstream and confirmed the PR diff changes only this study.
Staged privacy/path scans found no personal paths, credentials, or private
coordination identifiers. No direct main push, force-push, or self-merge occurred.

Read-only reciprocal review is complete; the integration coordinator will perform
the merge decision. Opening this PR is not integration or contest submission.
The deterministic validation remains 105 passing tests and six audited synthetic
runs, with zero experimental model calls. Future empirical work remains blocked
on an approved interface, configuration, budget and fresh prospective holdout.

## 2026-11-08 — Authorized live-stage preparation

After explicit start authorization, fetched upstream and created
`study/wrong-goal-proof-live-v1` from main `afd055c`, preserving the prior branch.
The baseline 105 tests passed in 4.375 seconds. Allocation for this study is USD20,
not the combined project budget. Core schedule remains 52 pilot +260 evaluation;
up to 15 identical technical retries and one genuine-interface-correction pilot
are reserved within the same allocation. No extra model or experimental arm.

Credential availability and the common coordinator preflight remain blockers to
acquisition. Preparation adds cross-bundle exclusions and a separately audited
live transport/ledger while preserving offline-only guards. No secret attachment,
credential bypass, or inference attempt occurred during this preparation.

## 2026-11-08 — Live preparation and 146-test validation

Implemented the separate official-HTTP acquisition path, strict live/campaign
audit, immutable preparation/freeze commands, cross-bundle exclusions and actual
translator-output/main separation check. The persistent hash-chained wallet
reserves before HTTP, fsyncs, retains unknown/abandoned charges, and enforces the
USD20 /379-attempt /15-extra-technical-attempt limits across stages and restarts.
Requested completion cap and the approved financial output margin are separate.
Provider identity, data policy, no fallback/redirect, receipt/request binding,
duplicate acquisition IDs and actual pilot/ledger binding are checked explicitly.

The original offline auditor was not widened to admit live metadata. Transport
fixtures cannot qualify a real pilot, revision or freeze. Mathematical evidence
verification remains separate from provider-origin claims. The union of actual
candidate functions from all preserved pilots is checked against main. Collision
blocks freeze and cannot justify a repeated pilot; no post-outcome automatic
resampling exists. Solver/scalar/vector/certificate algorithms did not change.
No extra experimental model or arm was introduced.

Exact final command:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=studies/wrong-goal-proof python3 -m unittest discover -s studies/wrong-goal-proof/tests -q`.
Result: **146 tests passed in 20.539 seconds**, Python 3.14.6 (105 original tests
+41 new tests). `git diff --check` and `run_live.py --help` also passed.
An earlier 128-test run found a Decimal reservation bug; it was corrected.
The expanded 144-test run initially exposed two test-harness assertions, which
were corrected; the complete 144-test rerun passed before the leakage tests.
Read-only peer review independently identified the Decimal issue and the omitted
first-pilot exclusion in the repeat path. Both fixes were independently reread;
the reviewer did not run this suite or assert live API access.

All new calls were explicitly labeled, in-process transport fixtures in unit
tests. **Actual experimental model requests: 0; new external experimental cost:
USD0.** Assistant-session costs are not measured or claimed to be zero. No secret
attachment/read/bypass was attempted. Approved credential availability and final
tariff/settings/source-bound coordinator GO remain unresolved. No real pilot,
main evaluation, findings, or empirical PDF is claimed. These are external
blockers, not a reason to invent another synthetic experiment. Public LIVE.md
documents the intended authorized commands. Upstream was fetched before preparing
publication; only this study's paths are being changed.
