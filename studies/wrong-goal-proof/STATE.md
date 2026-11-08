# Study state

As of 2026-11-08 UTC. Source: implementation and local test commands;
classification: PROJECT_REPORTED. This is an engineering record, not model evidence.

- Implemented a self-contained Python/stdlib Boolean-contract testbed, independent
  scalar/vector semantics, exhaustive certificates, seeded disjoint datasets,
  natural translation and paired certificate replay, offline adapters, manifest,
  incremental logging, freeze rehearsal, audit, and paired analysis.
- Latest complete test pass: 171 tests, Python 3.14.6, 28.092 seconds. This includes
  the original 105 tests plus 66 live-interface/exclusion/ledger/SSE/pacing tests.
- No experimental model calls, paid batches, or competition submission.
- A separate live HTTP interface, persistent USD20 wallet, source/configuration/
  manifest-bound GO, actual-pilot freeze and campaign auditor are implemented.
  The renewed authorized experiment now targets Qwen3.5-122B-A10B via Alibaba.
  Credential access has been restored; the compatible provider/settings/pricing/
  data-policy and budget admission preflight is in progress. Offline replay does not attest
  external acquisition chronology, and fixtures cannot qualify a live freeze.
- Read-only peer review found no C/Q-vs-closed-truth blocker. Its request/response
  consistency recommendation is implemented and passes regression tests.
- Six saved synthetic CLI runs passed audit: 728 local adapter invocations,
  616 reviewer outcomes, no model calls. Two complete 260-invocation engineering
  holdouts used perfect/local-only doubles. Abstain/malformed development runs
  correctly failed the freeze gate and did not proceed to holdout.
- Standalone evidence verification passed for all 40 planted originals and 120
  scripted false SAFE answers. Scope contrasts are zero in both doubles by design;
  no empirical claim follows. See VALIDATION.md and results/RECORD.json.
- Implementation commit: `c15e8401a9c41f4bf73deee3a02bdbf82394cc47`.
- Prior offline implementation: pull request
  https://github.com/RuslansAleksejevs/boundary-conditions/pull/2 was integrated
  upstream by the coordinator. The live additions are on the separate branch
  `study/wrong-goal-proof-live-v1`, published as draft
  https://github.com/RuslansAleksejevs/boundary-conditions/pull/4, not yet integrated.
  Live implementation commit: `040b36dbd203e34c9f80180c266ea413e028b90c`.

Next: obtain the exact source-bound acquisition GO after the successful
pre-inference SSE compatibility tests. Credential access is restored. No real model
pilot, empirical freeze, main evaluation or empirical report/PDF exists yet.

## Earlier preparation — 8 November 2026 UTC, before restored access

The offline PR is integrated upstream. Work continues on
`study/wrong-goal-proof-live-v1`, based on the refreshed main branch. Baseline:
105 tests passed in 4.375 seconds before live additions.

User-authorized experimental allocation: at most USD20 for this study, 312 core
role calls, at most 15 technical retries and one conditional 52-call corrected
pilot (379 attempts maximum). The experimental model/provider configuration and
common acquisition preflight are not yet finalized. Credential access is blocked;
no attachment attempt, credential workaround or experimental request was made.

Completed: exact cross-bundle exclusions (12 legacy bundles plus two inspected
transport-test recipes), a small official HTTP adapter, conservative persistent
budget reservation, separate live acquisition/campaign audits, actual-pilot
freeze, reproducible CLI, and live counterexample packets. The gate additionally
checks actual translated C/Q functions from all preserved pilots against future
main cases; collision stops freeze and cannot justify a repeat or automatic
resampling. Existing scalar/vector/certificate logic is unchanged;
offline execution/audit continue rejecting live adapters and nonzero model calls.
Read-only peer review closed the Decimal reservation defect and the first-pilot
exclusion omission in the conditional-repeat path. It confirmed budget, routing,
source/pilot binding and audit controls, without claiming provider capability or
price verification. Tests use explicitly labeled no-network fixtures only.
No new model findings or empirical report exist yet.

## Renewed live execution — 8 November 2026, 11:40 PST

The user explicitly authorized continuation and results publication and selected
Qwen3.5-122B-A10B via OpenRouter/Alibaba. The previously unavailable approved
credential is now attached through the ordinary secret mechanism. No raw value
was requested, copied or printed. The researcher session and existing branch/PR
are unchanged; no new model calls have occurred yet.

The Qwen endpoint supports enabled reasoning, not the previously proposed effort
parameter, and requires streaming in thinking mode. Final reservations cover the
entire 262,144-token context separately for input and billed output at verified
USD0.26/2.08 per million: USD0.61341696 per attempt. The narrower initial output
reservation was withdrawn before inference. The approved prospective amendment
removes only the full-campaign upfront-fit requirement; the hard USD20 wallet,
fixed 312-call core schedule and 379-attempt ceiling are unchanged. Budget stops
leave unassessed outcomes, never an adaptive smaller sample.

Bounded SSE with final usage, finish and DONE, reasoning-text removal, and a
180-second wall deadline is implemented. Billing settlement is separate from
reported API cost and conservatively uses the larger of that cost and the
no-cache token-price bound. Malformed/partial/missing-cost billing keeps the full
unknown-charge reservation. The final 159-test suite passed. Exact source-bound
GO and fresh campaign preparation are the remaining pre-inference steps.

Before this study's first inference, the companion study observed OpenRouter
repeating an identical empty terminal choice in its final usage event. The
parser now accepts exactly that final idempotent footer and rejects changed
finish/native-finish, extra delta fields, hidden continuation, or earlier/extra
terminal repeats. A sanitized, explicitly attributed interface fixture is
included in the source inventory. The initial unused preparation is preserved;
its replacement uses the same seed and dataset, with no outcome-based resampling
and no use of the conditional pilot-repeat allowance.

The companion subsequently encountered HTTP 429 and stopped. Before this study's
first request, a further prospective operational amendment added monotonic 20s
minimum attempt-start spacing and a 60s minimum 429 cooldown, honoring valid
Retry-After up to 300s and stopping above that bound. Waits are chunked at 30s.
No model/profile, prompt, task, gate, sample, quota or attempt limit changed. Only
safe normalized Retry-After and allowlisted error diagnostics are retained. The
first two unused preflights remain preserved; a new immutable preparation with
the identical dataset will bind the amended source and explicit pacing policy.
