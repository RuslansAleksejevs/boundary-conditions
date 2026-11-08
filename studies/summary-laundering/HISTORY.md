# Study history

## 2026-11-08 UTC — offline implementation and pre-observation amendments

Implemented the synthetic generator, strict JSON action batch, in-memory event
scorer, source/summary replay, two soft defense comparisons, reset allowlist replay,
bounded technical retries, versioned manifests and auditable logs. Added paired
statistics with missingness bounds, utility and uncertainty. Public code is
self-contained in this study and uses Python's standard library only.

Read the existing plan and related-work notes, and rechecked the two closest
official arXiv abstracts. Clarified that S-P/E-P measures a transformation bundle,
not pure paraphrasing. Defined byte-length matching and transient-effect scoring.
Corrected clean-pair selection to include lookup and arithmetic before any model
observations. Added controls against metadata forgery and trace manipulation.

The first unittest invocation failed because a fixture named `run` shadowed
`unittest.TestCase.run`; renamed it to `run_data`. The next invocation passed all
76 tests. An expanded integrity suite then passed 81 tests. These are software
tests, not LLM observations. Later validation is recorded as a new entry.

No paid API, new model batch, live-service target, empirical pilot, empirical
freeze, holdout or submission was performed. Current model access/budget are a
specific external blocker. Read-only peer review was requested; branch publication
is pending. Prior history is retained rather than silently rewriting results.

## 2026-11-08 UTC — peer fixes and final CPU validation

The read-only peer review found that test-double behavior could disagree with
the manifest profile, and that usage/cost metadata needed strict validation.
Bound profile and version at execution, validate response metadata in replay and
audit, and add regression tests. Also reject unpaired Unicode surrogate action
values and corrupted summary/failure records. Clean controls now cover both
task types and the development families. Added a conservative nondegenerate
bounded-cluster interval alongside the explicitly limited percentile bootstrap.

Final command: `python3 -m unittest discover -s studies/summary-laundering/tests -v`.
Result: **90 tests passed**, Python 3.14.6, observed 1.238 seconds. Ran all seven
development CLI profiles at seed 1701 and the 60-input engineering-validation
profile at seed 2802. All eight audits passed. Counts and precise reproduction
commands are in VALIDATION.md. Raw logs remain private, outside this repository.

No experimental API requests, paid batch, empirical pilot, empirical freeze,
scientific holdout, or contest submission occurred. Test doubles are prominently
marked as engineering-only. The live experiment remains blocked on an approved
model interface and explicit bounded-spending authorization. Fetched origin
before preparing publication; no shared branch or other study was modified.