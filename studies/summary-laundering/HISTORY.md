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

## 2026-11-08 UTC — branch published and pull request opened

Committed the implementation as `5bf037c1c0587510c69740f267ca3f8f76041cd1` and
pushed `study/summary-laundering` without force. Opened
[pull request #1](https://github.com/RuslansAleksejevs/boundary-conditions/pull/1)
against main. All 17 published paths were under this study. Staged whitespace and
private-path/credential-pattern checks passed; the commit uses a GitHub noreply
address. Raw logs, coordination identifiers and personal paths were not published.

The branch is ready for integration review, not claimed to be integrated into
main. The implementation worker did not merge the PR or edit shared repository
documents. Publication is not competition submission. The empirical model-access
and bounded-budget blocker remains unchanged.

## 2026-11-08 UTC — authorized live-stage preparation

Received explicit continuation authority and the study-specific USD 30 hard cap.
Fetched origin and created `study/summary-laundering-live-v1` from main `afd055c`
in the existing clean worktree, retaining the previous branch. Read the updated
execution/access instructions and shared next-experiment protocol. Credential
availability is blocked; no attachment workaround or model call was attempted.

Added initial OpenRouter/Together transport, a persistent Decimal reservation
wallet, exact live request/event/spend audit, fresh task values, saved randomized
condition order, clean-first pilot and code/config/pilot-bound main preparation.
Existing offline-only evidence gates were not removed. Directly reread official
routing/reasoning accounting documentation, including output-cap caveats.

Legacy suite: 90/90 PASS (0.820 seconds). Initial targeted tests exposed a Decimal
type acceptance mistake and a local status-helper naming collision; both were
corrected. Expanded suite: 114/114 PASS (1.797 seconds), entirely with local
fixtures. Additional HTTP serialization regressions and read-only peer review
are underway. Parameters in tests are fixtures, not an approved live configuration.
Actual acquisition, empirical freeze, main evaluation and report remain pending
the exact coordinator preflight and approved credential availability.

## 2026-11-08 UTC — live-contract review and local validation

Completed a 123-test HTTP-free suite (2.281 seconds) and a clean whitespace check.
Read-only peer review identified two current receipt-integrity gaps: retry flags
were accepted without recomputing eligibility, and acquisition IDs could be empty
or duplicated. Fixed both, added regression tests, and also validate assistant
role, unsolicited native tool calls and exact total-token accounting. A duplicate
provider ID stops subsequent dispatch and invalidates the run audit. Earlier
review notes referring to a different snapshot were explicitly withdrawn.

Added configuration-and-code-bound GO validation, actual pilot/ledger-prefix
re-audit before main acquisition, persistent cross-stage retry-limit tests and
explicit output-cap-overshoot counts. All core state/action scoring, attack
templates and hypotheses are unchanged. Credential lookup now follows all local
pilot-binding checks as well as the GO check. Final independent confirmation and
exact model/provider/sampling/tariff preflight remain pending.

No model request, credential-attachment attempt, real pilot, main acquisition,
scientific result, PDF result report or competition submission occurred. This
is preparation for the authorized empirical stage, not its completion.

The read-only peer subsequently confirmed both current findings closed against
the exact updated source hashes, without claiming to have rerun the test suite.
No remaining blocker was found in those reviewed sections. This confirmation is
not approval of provider pricing, credentials, or empirical acquisition.