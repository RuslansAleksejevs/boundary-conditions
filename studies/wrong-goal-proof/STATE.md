# Study state

## Current editorial phase — 9 November 2026 UTC

The completed empirical release was integrated through PR #4, merge
`755e51475e343825c67e142cbbe34aff2f22f9b3`. A new reader-first report is prepared
on `study/wrong-goal-proof-reader-report`, based on main
`7e2780c1357dcb0ce14b749caf222fd1080bad06`. It is an editorial release only:
no new model calls, revised scoring, rewritten data or competition submission.
The new location is `reports/reader/verified-but-what.pdf`; the earlier pilot
and main PDFs/TeX, frozen source and data remain byte-for-byte preserved.

The six-page reader PDF has a 209-word abstract, a clickable page-one repository
link, explicit result/uncertainty tables and two actual source-bound examples.
SHA256: `c8bf9d451609a49e2f1a159a24a9d4a9adf58d57b4eeb6f616c259932c7e9d78`.
Cached Tectonic 0.16.9 built it without warnings; every page was visually checked.
The 171 scientific, 28 existing reporting and 12 new reader-binding tests passed.
Both native analyses and the campaign/evidence checks passed without new model
requests; all 91 protected old files are unchanged. Full commands and results
are in [reader release checks](reports/reader/CHECKS.md).

The landing page and report guide now prioritize question, result, PDF, data and
offline replay. Detailed earlier guide text is retained separately. Read-only
integration and peer reviews found no blocker. The peer's C-versus-Q wording
clarification was accepted without changing formulas or results. Publication of
the separate editorial PR is next. Human author review remains pending.

The detailed acquisition checkpoints below are historical. Their earlier
pending-merge statements describe those checkpoints, not current integration.

## Completed empirical record and historical checkpoints

As of 2026-11-09 UTC. Source: implementation and local test commands;
classification: PROJECT_REPORTED. Engineering fixtures and actual model
observations are explicitly separated below.

- Implemented a self-contained Python/stdlib Boolean-contract testbed, independent
  scalar/vector semantics, exhaustive certificates, seeded disjoint datasets,
  natural translation and paired certificate replay, offline adapters, manifest,
  incremental logging, freeze rehearsal, audit, and paired analysis.
- Latest complete test pass: 171 tests, Python 3.14.6, 21.591 seconds. This includes
  the original 105 tests plus 66 live-interface/exclusion/ledger/SSE/pacing tests.
  A separate reporting/accounting suite passed 28 tests in 0.289 seconds.
- The original live pilot is complete: 51 actual HTTP200 calls for 52 scheduled
  roles; 50 schema-completed, one invalid translation and one dependent blocked
  review. Known API cost and conservative settled wallet both USD0.39923650,
  with zero technical retries, HTTP429, unknown charges or pricing overruns.
  Main began at 21:51:10Z after renewed authorization and ended at 23:44:59Z:
  100 originals, 260 scheduled roles, 259 physical attempts, 253 schema-valid
  responses, four schema errors and three blocked dependent reviews.
- Completed main: natural utility 36/40, semantic C/Q drift 0/37 valid
  translations, false SAFE 0/36 assessed natural reviews; B/N/S each correctly
  answered all 40 planted originals and all 20 equivalent controls. No observed
  false guarantee or abstention. Both paired fault contrasts are zero on 40
  complete pairs; bootstrap [0,0] does not establish equivalence. The bounded-iid
  interval is approximately [-0.4294694,0.4294694], with independence and transfer
  beyond shared templates unestablished.
- Campaign known reported cost and conservative settlements: USD2.39640830 for
  308/310 attempts. Two HTTP429 costs remain UNKNOWN, with USD1.22683392 full
  holds and USD3.62324222 cumulative commitment. No unsettled reservation or
  pricing overrun. Both existing-policy retries used identical same-role payloads.
- A separate live HTTP interface, persistent USD20 wallet, source/configuration/
  manifest-bound GO, actual-pilot freeze and campaign auditor are implemented.
  The renewed authorized experiment now targets Qwen3.5-122B-A10B via Alibaba.
  Credential access and the exact paced pilot GO have been verified. Offline replay does not attest
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
  Frozen acquisition commit: `83aa8ee313d4f054ac47af038a8b5c33a6a1e859`.

Main release commit `7c7c7ecdc422bb384cf588adc587971e1af46f6c` was pushed to
existing draft PR #4 on 9 November 2026 UTC. It is not yet integrated.
Next: coordinator integration and human author review. No more model acquisition or
competition submission is authorized. The full private and exported native
campaign audits, empty false-guarantee evidence check, journal bindings and exact
approved scientific GO comparison all passed. The public complete campaign is
in `results/live-main-2026-11-08/`; the standalone English report is in
`reports/main/` (seven-page PDF, 211-word abstract, no TeX warnings, required
ethics and AI-use disclosures). The public export has 14 hash-inventoried files.
All visible main answers and publication-boundary patterns were reviewed.

The historical pilot PDF is preserved byte-for-byte at its published version;
its README records the exact presentation-source revision. Current main wording
clarifies the oracle's trusted-AST/computation privilege without suggesting hidden
original-task semantics. Neither report has been submitted. Frozen acquisition
commit remains `83aa8ee313d4f054ac47af038a8b5c33a6a1e859`; its source inventory is
87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e.

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

## Live pilot checkpoint — 8 November 2026 UTC

Exact paced source/configuration/manifest GO was issued before the first request.
The approved official API acquisition began at 20:36:59Z, using only the ordinary
reviewed secret attachment and synthetic tasks. First two natural originals were
correctly translated (C and Q unchanged as open functions) and correctly answered.
The full pilot is still running; this is not a freeze decision or selected sample.
The source inventory remains frozen. A presentation-only SVG/PDF figure renderer
outside the acquisition inventory passed four fabricated-count/no-network tests;
those tests are not additional model evidence or generated empirical figures.

## Completed pilot and prospective freeze — 8 November 2026 UTC

Pilot started20:36:59.031008Z and finished20:59:48.911404Z (1369.875s). Natural
originals were solved7/8; open C/Q drift was0/7 valid translations, with one
malformed JSON translation left unassessed. B/N/S each produced0/8 false SAFE
on planted faults and8/8 valid UNSAFE witnesses; equivalent utility was4/4 each.
No reviewer abstention occurred. The zero paired difference is only a development
result; its zero bootstrap interval is degenerate, not proof of no effect.
Actual-pilot/holdout comparison found19 distinct candidate functions and0 overlaps.
The original invalid and blocked roles are preserved; no repeat was requested.

Input tokens42437, output186636, reasoning184388; all51 costs known. Main remains
260 logical roles on100 unchanged held-out originals. Mean/observed-max campaign
cost projections are aboutUSD2.552/4.106, not guaranteed bounds. The observed-wall
projection is about116.4min for260 attempts, versus215.3min for275 at the observed
maximum latency. Hard-wallet/time risks and the reporting reserve remain explicit.

Pilot run hash: `f696c9be737a22278b76b7f1bfa91527b1e8a23226ea5914e93e70b4111fb2c1`.
Freeze hash: `e5b6cc5c66c3698284e5af2145add1983a02b195067c23ef920c7a1c766dab7a`.
Source inventory remains `87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e`.
The first empirical pilot figure was generated from audited analysis and visually
checked; it explicitly says development pilot, not confirmatory. Separate local
PDF toolchain validation also passed. Report source follows the official template
but cannot compile as an empirical paper until actual result text is supplied.

## Presentation checkpoint — 8 November 2026, 21:24 UTC

Nine presentation/export tests passed in0.003s using fabricated counts and
no network; these tests are additional to the171 acquisition tests. The
coordinator reviewed the report, exporter and chart code without a blocking
finding. Export still requires an ended main run and a real end-to-end audit
before publication; no held-out task data has been released.

A private six-page pilot-only PDF compiled with Tectonic0.16.9 using cached
packages. Its240-word abstract, mandatory ethics appendix, AI-use statement,
human author spelling and lack of private paths in extracted text were checked.
The larger-font chart and table were visually checked in-page; compilation had
no overfull warnings. This preview reports only the actual development pilot
and explicitly states that main is pending. The frozen source inventory remains
unchanged. Main GO and the serialized API-route handoff are still pending.

An unchanged-source CPU rerun passed171 tests in21.834s and9 presentation tests
in0.004s. Pilot campaign audit passed again with51 physical calls and unchanged
USD0.39923650. Source digest remains87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e.

## Main execution blocked before dispatch — 8 November 2026, 21:31 UTC

The companion released the shared route, and a source/configuration/manifest-
bound main-only GO was issued at21:29:15Z. The exact main preflight passed.
The execution permission layer then denied the paid260-role acquisition before
launch, requiring new direct user authorization beyond the delegated scientific
GO. No alternate route, split call sequence or retry was attempted. The route
was released to the coordinator while this external permission blocker remains.

Read-only checks at21:31:08Z confirm no main directory, the original102-event
pilot wallet,51 physical calls and unchangedUSD0.39923650. Campaign audit passes.
No holdout data or answers have been published. The frozen sample and source
remain unchanged; a future run still needs explicit permitted execution and an
exclusive-route handoff. The pilot-only report preview is not a completed
held-out report, and PR#4 remains unmerged.

## Development-only publication preparation — 8 November 2026

The portable English pilot-only PDF/Markdown and figure are prepared under
`reports/pilot/`. The public view under `results/live-pilot-2026-11-08/` contains
20 development originals and exact visible pilot records, not the 100 unstarted
held-out tasks or the full source dataset. Its limited verifier passes with
52 roles, 44 outcomes and zero false guarantees; it reruns mathematical scoring,
aggregate analysis and physical-receipt usage but explicitly does not reproduce
the complete acquisition or cross-split audit without the withheld corpus.

Eighteen presentation/publication tests passed in 0.284 s, additional to the
171 acquisition tests. Read-only peer review reran the public check and found no
scientific blocker; the exact scientific pilot authorization paragraph's public
scope was confirmed by comparison with the private original. All 51 visible answers were manually
checked; no private paths, credentials or hidden reasoning were found. Natural
false-SAFE display now states 0/7 assessed, alongside 7/8 scheduled correct and
one unassessed review; no outcome or scoring rule changed. Acquisition source
and USD 0.39923650 remain unchanged. Main execution is still blocked.

## Authorized main started — 8 November 2026, 21:51 UTC

After renewed stage-specific user authorization, the execution-owning context
submitted the exact previously denied command once for a fresh review. It passed
and started the single main process at 21:51:10.093347Z. This study worker only
reads the existing journal; it did not submit a duplicate API command or change
source, configuration, tasks, scoring or sample. The fixed 100 originals and
260 roles remain in scope, under the same USD20 wallet and retry/circuit limits.

Read-only early checkpoint at 21:52:35.436624Z: three HTTP200 receipts, all three
schema-completed, known main cost USD0.02207062, one additional request in flight.
The recorded model/provider is Qwen3.5-122B-A10B/Alibaba, complete SSE, observed
minimum attempt-start gap22.670035s. These are operational observations, not a
completed scientific main result. The acquisition inventory remains unchanged.
Only the separately dated pilot view/report may be published until main ends.

At 21:58:31Z, the existing main journal contained 17 HTTP200 receipts and
17 schema-completed roles, all costs known, totaling USD0.12502880 for main only.
No completed main run file existed. The pilot-only update was committed and
pushed to PR#4 after staged scope/privacy, append-only history and PDF checks.
The final reporting-test rerun passed 18 tests in0.292s. The PR description now
distinguishes the completed pilot from the ongoing main; no self-merge occurred.

At22:10:57Z, main had47 HTTP200 receipts with known costUSD0.37256648. Its first
translator-format failure was malformed JSON (438 visible characters); the
dependent review was blocked, not retried. Processed logical statuses were
46 completed, one schema error and one blocked translation-dependent review.
This is a preserved normal outcome, not demonstrated C/Q drift or a transport
stop. Acquisition continues under the unchanged schedule. The current public
branch also includes documentation-only status clarification commit3832913.

At22:33:55Z, main had100 HTTP200 receipts, all costs known, totaling
USD0.77680018 for main (USD1.17603668 including the completed pilot). Its101
processed logical roles were98 completed, two schema errors and one dependent
blocked review. The second malformed response was a reviewer answer, retained
without repair. There was no transport failure or completed main run file.
The exact purpose-written main authorization paragraph has now been separately
approved for eventual publication after completed-run audits and content review;
no private confirmation record or coordination text is included in that scope.

At22:46:45Z, main reached125 HTTP200 receipts/126 processed roles, with123
schema-valid responses, the same two schema failures and one dependent blocked
review. Known main cost was USD1.01474282; no transport error or completed run
file was observed. Reporting source now clarifies that the oracle's privilege
is a trusted structured original-AST interface and exhaustive computation, not
secret original-task semantics. All reviewers see the full controlled original.
This is a wording correction only, not a protocol/input/scoring change; it will
be checked in the final report build. The published pilot PDF remains unchanged.

At23:12:04Z, main had183 physical receipts:181 HTTP200 and two HTTP429.
Known main cost was USD1.42809550 across181 charged receipts; the two429 costs
remain UNKNOWN, with both full-context conservative wallet holds retained.
The184 processed scheduled roles comprise177 completed, four schema failures
and three dependent blocked reviews. The two additional malformed translator
responses were preserved without repair or semantic retry.

The429s at22:55:37Z and22:57:26Z each recovered on the existing automatic
same-role retry after at least60s. This is not a new API process or a change to
the frozen retry policy; exact payload equality and full pacing will be checked
in the final audit. The provider returned only error code429, so its cause is
unknown. No completed main run file or final scientific result exists yet.

At23:17:32Z,200 of260 scheduled roles were processed:193 completed, four schema
failures and three blocked dependent reviews. There were199 physical receipts
(197 HTTP200, two HTTP429), with known main cost USD1.51224684 and the same two
unknown charges. No new failure, stop or completed run file was observed.

The report-only `acquisition_summary.py` now requires an ended main, full native
campaign audit and matching acquisition inventory. It separates decimal reported
API costs, conservative settlements, unknown full holds and unsettled reserves;
it also reproduces actual UTC request gaps and exact-payload technical retries.
Twenty-eight reporting tests passed in0.287s, including eight simple accounting
fixtures and two replays of already-published pilot metadata. No new model calls,
task generation or scientific analysis were performed. The source inventory is
still87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e.

At23:35:55Z,240 of260 logical roles were processed (233 completed, four schema
errors, three blocked reviews), using239 physical receipts (237 HTTP200,
two429). Known main cost was USD1.84807792; two unknown full holds remain.
No new failure, halt or completed run file was observed. Independent read-only
review repeated all28 reporting tests in0.293s without a blocker. Its decimal
wording clarification was applied: the helper converts each parsed provider
cost through Decimal, not an original JSON wire lexeme. Report prose also
distinguishes scheduled roles from physical attempts and makes uncertainty
assumptions explicit; no frozen acquisition or scoring source changed.

## Completed main and full release checks — 8 November 2026, after 23:44 UTC

The sole acquisition process exited successfully after the unchanged 260-role
schedule. Main run digest:
`81af66525adfb197fb3c48911fb07c05c3668fa8f7c75987a6143aac54a636de`.
Native private/public audits agree on 259 main and 310 cumulative physical
attempts, 220 main reviewer outcomes and zero false guarantees. Main private
journal equality covers all calls, receipts, outcomes and the terminal hash
(1000 events); the pilot likewise matches its 200 events. The preserved main GO
object matches the exported run, and its original file SHA256 remains
`55b13ad6cc7822751333c62ad101792acc5865cc0891c57d3bf63452de76f523`.

All four unassessed natural originals were SAFE: three translations were malformed
JSON and one review included Markdown fences. These are not repaired, resampled
or counted as semantic drift. The frozen generic natural missingness bounds
[0,0.10] remain unchanged. All 20 natural UNSAFE witnesses and 120 planted-arm
witnesses independently pass. Equivalent utility is 20/20 per arm; clean-original
utility is 56/60. The false-guarantee packet is correctly empty.

The two exact-payload retries began 60.004940 and 60.004454 seconds after their
HTTP429 receipts. Minimum observed UTC start spacing is 20.000076 seconds;
monotonic elapsed main duration is 6829.286533 seconds. Known main cost is
USD1.99717180; two failed-attempt costs and token usages remain unknown. Two
responses reported 10,723 and 8,283 output tokens against requested 8192, within
the prospectively reserved full context; neither was reported truncated.

Full export and operational summary reproduced the audits with zero new API
calls. Every inventoried byte/canonical digest passed; public/private main and
operational summaries match exactly. All 37 valid translator texts, all 39 unique
valid reviewer texts covering 216 responses, and all four malformed answers
were manually read; no private content was found. Seven-page main PDF title,
results/figure and mandatory appendix were visually checked after a warning-free
cached Tectonic 0.16.9 build. Its abstract contains 211 whitespace-delimited words.
An incidental rebuild of the pilot presentation was restored to its exact
historical published PDF; source-version guidance now prevents silent replacement.
Independent coordinator and peer reviews found no blocking claim, provenance,
privacy or denominator issue. Independent tests passed 171 in 21.312 seconds
and 28 in 0.281 seconds; both reviewers also repeated public campaign/evidence
checks. No private account data or additional model observations are published.
