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

## 2026-11-08 UTC — live preparation published as a draft

Fetched origin, reviewed all 14 staged paths and their content, and passed
whitespace and private-path/credential-pattern checks. Committed the preparation
as `4030c75c16f88b4add9e652073e8ba0216344d34`, pushed
`study/summary-laundering-live-v1` without force, and opened
[draft pull request #3](https://github.com/RuslansAleksejevs/boundary-conditions/pull/3).
No other study, shared repository file or shared branch was modified. No merge
was performed. The draft explicitly states that actual model acquisition and
scientific results remain blocked on exact preflight and approved access.

## 2026-11-08 UTC — user-selected Qwen route before acquisition

Execution authority was renewed, approved secret availability was independently
reported by the coordinator, and the user selected Qwen3.5-122B-A10B through
OpenRouter/Alibaba. No model had yet been called; this is not model selection
based on observed attack success. Retained the existing live branch and PR.

Reread the public endpoint listing, reasoning API documentation and the relevant
official model-card sections. Replaced the unsupported effort field with explicit
reasoning enablement, added top-p, and fixed the full-context reservation to
262,144 tokens. The per-call wallet and unknown-charge rules were not weakened.
The old 123-test suite passed after compatibility changes (2.066 seconds).

Before selecting actual inputs, noticed that an illustrative pilot seed matched
an inspected interface fixture. Added explicit fixture exclusions; prospective
seeds 2026110811 (pilot) and 2026110812 (main) passed ID/fact/raw-text separation.
Attack templates, task policy, scorer and primary hypotheses are unchanged.
Final configuration/GO and actual pilot remain pending; model requests: zero.

## 2026-11-08 UTC — final streaming and conservative budget preflight

Primary native-provider documentation exposed two compatibility assumptions:
thinking for this open-weight endpoint requires streaming, and native max_tokens
does not reliably bound billed reasoning. Before any inference, switched to SSE
and a source-bound full-native-context output reserve. The hard USD 30 wallet,
fixed schedule and no-outcome-tuning rule remain unchanged. Confirmed unused
reserve can be released; unknown charges remain reserved and budget stops leave
scheduled outcomes missing. Completion of the full schedule is not guaranteed
under worst-case token use.

Added bounded SSE assembly with immediate reasoning-field removal, identity
consistency, final usage, terminal finish and DONE requirements. A three-failed-
logical-transport circuit preserves remaining missing cells during an outage.
No native JSON override, task-prompt change or alternative model/provider was added.

Final local validation: 131/131 tests PASS (1.960 seconds); the coordinator
independently reported 131/131 PASS (1.951 seconds). All tests are HTTP-free.
The prospective profile uses temperature 0.6, top-p 0.95, requested max_tokens
8,192, reasoning enabled/excluded, 180-second timeout and explicit data retention
allowance for synthetic inputs only. Exact code/config/manifest GO remains
separate. Actual model calls and experimental cost at this milestone: zero.

## 2026-11-08 UTC — final peer billing/context fixes before GO

Focused peer review found that an invalid provider envelope could release a
reservation before all route/identity/usage/finish checks had passed. Delayed
financial settlement eligibility until full validation; malformed billing stays
unknown and fully reserved. Added the joint input-plus-completion context check,
not only separate input/output bounds. Validly billed truncations and refusals
remain unsuccessful model outcomes without unnecessary financial uncertainty.

Final suite: 133/133 PASS (1.957 seconds), with targeted regressions. The earlier
unused source-bound GO was withdrawn before any inference, and the pilot plan
will be regenerated under the corrected source hash. Configuration, sample seed,
prompts, scorer and monetary cap are unchanged. Actual model calls remain zero.