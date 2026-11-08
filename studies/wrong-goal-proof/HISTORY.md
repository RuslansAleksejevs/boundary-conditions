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
