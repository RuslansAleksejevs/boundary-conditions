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

## 2026-11-08 20:12 UTC — first real pilot stopped on SSE compatibility

Exact source/configuration-bound GO was issued for commit `02e34e6`. Sent the
first planned clean-summary request through the approved OpenRouter/Alibaba
route. The response returned HTTP 200, the correct model/provider, a visible
answer, final usage and DONE in 16.575 seconds. The provider repeated the same
empty assistant `stop` chunk when adding usage; the strict parser rejected this
second finish marker. Acquisition stopped after one API request, without an
automatic retry, executor call or attacked input.

The immutable run audit passed; 0/108 role responses qualified and all 96
executor cells remain missing. Reported usage: 231 prompt tokens, 2,575 completion
tokens (2,531 reasoning), USD 0.00541606. The rejected receipt did not release
the full USD 0.61341696 wallet reservation. Hidden reasoning text was not retained.
This is an interface failure, not evidence for or against the research hypotheses.
Proposed a narrow terminal-usage compatibility repair and the one permitted
fresh repair pilot; no prompt, scorer, model or outcome-based tuning is proposed.

## 2026-11-08 UTC — approved narrow repair, validated without further inference

The coordinator independently inspected the failed receipt, confirmed its actual
USD 0.00541606 billing through read-only account reconciliation, and approved the
single permitted interface correction/repeat. The conservative USD 0.61341696
wallet hold is retained. No original outcome or financial record is rewritten.

The corrected assembler accepts only a final usage-bearing, idempotent empty
terminal repeat, with unchanged finish/native finish and identity; continued
content, refusal, tool calls, reasoning deltas or further events are rejected.
Added the sanitized real terminal pair and negative regressions. The local suite
passed 135/135 tests in 1.735 seconds. A read-only in-memory replay of the actual
14 sanitized events passed, and the original failed-run audit still passed.
No new API request was made during diagnosis or validation. Fresh repair-plan
seed, commit and source-bound GO are recorded separately before any repeat.

## 2026-11-08 UTC — repair pilot interrupted by provider rate limits

Ran the fresh repair pilot under commit `40280f6`, seed 2026110813 and a renewed
exact-source GO. The terminal-usage compatibility correction worked. There were
59 API attempts: 51 completed responses, eight HTTP 429 errors and five identical
technical retries. Acquisition stopped at the predeclared circuit of three
consecutive failed logical transports. No third pilot, resume or main run followed.

The immutable audit passed. The real pilot gate failed at 47/108 valid role
responses; clean correctness was 29/32. Four invalid executor batches, three
exhausted transport failures and every unattempted scheduled cell were retained.
Accepted repair receipts total USD 0.09577568; with the independently reconciled
first request, accounted billing is USD 0.10119174. Eight HTTP-error charges are
unresolved in local receipts. The unchanged wallet holds USD 5.61652832, including
full conservative reserves. Total real API attempts across both stages: 60.

At the coordinator's request, assessed—but did not implement—an explicit
operational continuation restricted to the exact 54 never-attempted remaining
roles. Existing outcomes would be immutable, no retries reallocated, and the
combined repair stage would remain within its original 113-attempt cap. This
requires an openly disclosed stop-rule/pacing amendment and separate union audit;
it cannot be called the unchanged original pilot. No attack-effect contrast was
inspected for this decision. Main freeze and holdout remain unperformed.

Prepared reporting-only exports and a trace-selection rule outside the frozen
acquisition inventory. Five pure reporting regressions bring the local suite
to 140 tests (2.655 seconds on the first expanded run). Exported pilot calculations
are labeled interrupted development evidence, not held-out findings.

## 2026-11-08 UTC — explicit operational amendment implemented, not yet executed

The coordinator authorized implementing the documented untouched-suffix recovery
after the provider outage. The original failed run/gate and all financial holds
remain immutable. A new plan-specific GO, bound append-only ledger stage and
separate composite audit prevent replaying any attempted response. Existing
scientific modules and ten generator/metric/receipt functions are byte-checked;
only orchestration, transport limits, ledger auditing and CLI entry points changed.

The continuation has zero new retries, 54 new logical roles at most and 113 total
repair-stage attempts. A fresh process pauses 20 seconds, then enforces at least
20 seconds between starts. Before freeze, aligned HTTP 429 handling to a minimum
60-second cooldown, normalized Retry-After up to 300 seconds and a stop beyond
that limit, with waits in chunks no longer than 30 seconds. Added a POSIX total
180-second wall timer. These operational safeguards are not evidence that the
unknown upstream rate-limit cause has been fixed.

Final local suite: 161/161 tests PASS in 4.836 seconds; all HTTP-free. The original
two real-run audits still pass. Focused peer review found no new blocker in the
initial continuation design; final aligned cooldown review is pending. No new
API request was sent. The shared provider route is reserved for the other study
until its checkpoint. Continuation and main each still require a separate GO.

## 2026-11-08 UTC — continuation ready after independent checks

Published commit `eb8844d` and froze the untouched-suffix continuation plan before
any new request. Final focused peer review closed the aligned cooldown and
composite-provenance changes without a new blocker. The coordinator independently
passed 161 tests in 4.674 seconds, audited both original real runs, checked frozen
scientific functions, the exact 54-role suffix, and the unchanged 123-event wallet
prefix. Execution remains unapproved only while the other study uses the route;
a separate exact plan-bound GO is still required. New API calls at this point: 0.

## 2026-11-08 21:07 UTC — authorized continuation started

The other study completed its pilot and released the provider route. A separate
GO issued at 21:06:16 UTC bound the exact immutable continuation plan and source
inventory at commit `eb8844d`. Started the one permitted 54-role continuation with
the existing wallet, zero new retries and unchanged scientific source. This is
an in-progress acquisition record, not a passing composite gate or main result.

## 2026-11-08 21:35 UTC — amended pilot completed; main frozen but not acquired

The authorized continuation exited successfully after exactly 54 new requests,
all completed, with zero new retries or transport failures. Of those new roles,
52 are valid. Its first request started at 21:08:04.652829 UTC and the last
finished at 21:26:27.112278 UTC. The minimum audited monotonic start spacing was
20.000119 seconds. The shared experimental route was explicitly released after
the acquisition process exited, before further reporting work.

The composite audit passes with 113 repaired-pilot attempts and 96 executor rows.
The original parent object, 59 calls and 123-event financial prefix are exact.
The original gate remains failed at 47/108; the explicitly amended composite
passes the unchanged gate at 99/108, with 29/32 correct clean cells. Six invalid
executor batches and three missing transport outcomes remain. There were no
observed forbidden effects or valid protected-write attempts; this is small
development evidence, not a held-out result or proof of safety.

Continuation billing is USD 0.12952160. Total accounted experimental billing,
including the separately reconciled first failed request, is USD 0.23071334
across 114 attempts. The unchanged conservative wallet totals USD 5.74604992,
with nine old unknown/rejected-receipt holds. Read-only account reconciliation
agrees with the continuation increment; it does not release financial holds.

After audit/gate PASS, the authorized CPU-only main freeze fixed the original
seed 2026110812 and 40 attacked plus 20 clean inputs, 540 core requests, 27
remaining technical retries and all unchanged scientific settings. The exact
manifest hash is recorded in results/MAIN_FREEZE.md. Independent checks verified
the manifest, actual composite binding and financial prefix. Main API execution
is paused pending renewed stage-specific user authorization. No main API call,
probe, new model selection, payload tuning or held-out corpus publication occurred.

Reporting-only tests now pass 166/166 in 5.994 seconds; the frozen acquisition
inventory is unchanged. A new schema-2 public export reproduces all 96 outcomes
from 113 visible call records and both primary contrasts without private access.
The original counts-only export remains unchanged. The composite has only seven
complete primary pairs and inadequate length matching (3/8 unmatched); the
pilot-only English draft reports those limitations rather than repairing the
comparison after observing results. It remains pending author and code review.

## 2026-11-08 UTC — pilot-only report and public review

Prepared the standalone English development report, a 208-word abstract and the
exact mandatory appendix heading, with no unconfirmed affiliation or final
author approval. The cached-only Tectonic 0.16.9 build has eight pages: six main
pages including references and two appendix pages. Fixed a missing cached circle
font by using an existing math glyph and corrected a long command's line break;
the reviewed build has no TeX warning. Visually inspected the title, complete
condition table, paired-uncertainty figure and reproduction command.

A peer read the entire manuscript, result text, methods, appendix, public checker
and exporter; independently reran the public checker successfully; and found no
blocking scientific or public-subset issue. This was focused read-only code and
claim review, not a full private acquisition audit or external empirical review.
The exact mandatory appendix heading was aligned following that review. A later
full local suite passed 166/166 tests in 5.844 seconds. Publication scans found
no personal paths, secret values, private coordination IDs, raw GO records or
provider generation IDs in the new data bundle. Frozen acquisition source stayed
unchanged; real API calls since the composite completion remain zero.

## 2026-11-08 21:49 UTC — pilot report published; main authority renewed

Committed and pushed the reviewed pilot-only report, eight-page PDF, schema-2
public evidence and reporting tests as `58bc90085f8d02cf14ba1947236a4c478e2045a8`
to the existing draft PR #3. Staged-path review covered only this study; fetch
preceded publication, and no merge, rebase, force-push or shared-file edit occurred.
The public main record contains hashes, not the held-out task corpus. PDF visible
text and bundle privacy scans passed. The report remains pending human author
review and is not integrated or submitted.

Renewed direct user authorization was then reported for the original main API
stage within the unchanged study/shared spending ceilings, including all pilots.
This study remains stopped until the other study releases the route and a new
exact-source GO is issued. No main API call or probe has been made. Updated only
current authorization wording, not the prospective main, source inventory or data.
The provider-reported 30-day logging/no-training/non-ZDR metadata was checked
against the dated preflight source and public execution-budget record; no verified
deletion guarantee is claimed. Experimental funding is contributor-provided.