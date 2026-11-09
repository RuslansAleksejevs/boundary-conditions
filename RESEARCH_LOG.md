# Research log

This is the detailed, original lab record. For a short account of what happened
and when, read the [timeline](TIMELINE.md). For the current reports and results,
start with the [overview](README.md).

Each entry describes its own checkpoint. Earlier statements such as “no model
experiments yet” are kept as history, not as the current status. Original entries
are not rewritten when later results arrive.

## 2026-11-07 — Repository foundation

- Established two separate study plans: summary laundering and certificate scope.
- Defined shared standards for exact scoring, frozen evaluation, uncertainty,
  utility, cost, and publication review.
- Added a focused reading list and explicit boundaries on novelty claims.
- Prepared an English public research record for Swarm Alignment Hackathon 2026.

**Evidence status:** no implementation, model experiments, or measured results yet.
The proposed combined budget is 960 model calls, including pilots; this is a
planning estimate, not executed work. Next: implement and test the local harnesses,
then run bounded pilots once model access and execution limits are settled.

## 2026-11-07 — Parallel implementation started

Both studies now have separate implementation workstreams and Git checkouts:
`study/summary-laundering` and `study/wrong-goal-proof`. Each owns its study
directory; shared documentation and integration remain with the coordinator.

The next deliverables are exact scorers, tested local harnesses, reproducible
commands, and explicitly labeled dry runs. Changes will be published through
separate pull requests with peer review and sequential integration. Model
evaluations require a confirmed interface and execution budget; none have run yet.

## 2026-11-08 — Study A integrated after independent review

[PR #1](https://github.com/RuslansAleksejevs/boundary-conditions/pull/1) was merged
at `9a01ded8d7d72ed4c333ff3e01683d850c45f773` after peer review and coordinator
review of the exact head `646cc284f43bb05f8e4967bf5860230259504bd9`.

The coordinator independently reproduced all **90 tests** (1.144 seconds), the
60-input / 480-outcome / 540-logical-call engineering validation, and a technical
failure rehearsal with 47 logical attempts and five identical retries. The
author's saved validation record also passed the audit. All 17 changed paths
were confined to Study A; no blocking integration findings remained.

The implementation records transient forbidden effects, preserves missingness,
binds replay inputs and configuration, and labels every synthetic output as
engineering-only. Method amendments explicitly distinguish a summary/extract
transformation bundle from a pure paraphrasing effect, and bytes from tokens.

**Zero external experimental model calls.** No scientific pilot, empirical
freeze, or held-out model evaluation has occurred. Study B's PR remains pending.

## 2026-11-08 — Study B integrated; live stage planned

[PR #2](https://github.com/RuslansAleksejevs/boundary-conditions/pull/2) was merged
at `3905e6a18ef929cc02e09494978e78b301d4c442`, with the reviewed head
`c5f0562f86d1c318d1c873939f27964c0a633610` unchanged. The coordinator independently
passed all **105 tests** and repeated six synthetic CLI runs, including correct
rejection of failed pilot profiles and standalone checking of 40 contracts /
120 scripted false guarantees. Peer review left no blocking code findings.
All 31 changed paths belonged to Study B. These are engineering results only.

Both implementations are now in main. The [next-stage plan](docs/NEXT_EXPERIMENTS.md)
keeps the 160-call combined live pilot and 800-call frozen evaluation core,
adds concrete access/budget and acquisition-integrity gates, and narrows the
development allowance to avoid outcome-driven tuning. Live transport, fresh
cases and prospective empirical freezes still need to be completed. No new
model calls or competition submission occurred while preparing this plan.

## 2026-11-08 — Live execution authorized; funding and model fixed

The contributor authorized paid acquisition and publication of the funding
record: **USD 50 total, allocated $30 to Study A and $20 to Study B**. A read-only
account check at 19:48 UTC confirmed $50 available and no prior usage. The target
is Qwen3.5-122B-A10B through OpenRouter with Alibaba fixed and fallbacks disabled.
The [execution record](docs/EXECUTION_BUDGET.md) specifies settings, privacy
conditions, and conservative per-request reservations.

Before any inference, the coordinator approved a prospective budget-admission
amendment: retain hard per-study stops and the original scheduled cases, but do
not require the entire campaign's full-context worst case to fit upfront.
Budget-stopped cases remain missing, not silently replaced or counted as safe.
Pilot viability and cost must be reviewed before the frozen evaluation.

The two existing workstreams are adapting and testing their live transports.
**Experimental calls: 0 at this snapshot.** Engineering tests and funding are
not model findings. No competition submission has been made by this project.

## 2026-11-08 — First model acquisition; throttling and explicit recovery amendment

Study A made one planned clean request, then used its one permitted interface
correction for an idempotent terminal SSE usage chunk. The failed original was
preserved. The repaired pilot made 59 attempts for 54 scheduled roles before
HTTP 429 responses triggered its declared three-failure stop. Audit passed;
the full-pilot gate failed at 47/108 valid roles, with clean correctness 29/32.
No held-out evaluation ran and no completed answer is being resampled.

A read-only account reconciliation at 20:27 UTC confirmed total actual API spend
of $0.10119174, not the larger conservative wallet reservations. The
[dated operational amendment](docs/OPERATIONAL_AMENDMENTS.md) specifies paced,
serialized acquisition and a separately audited continuation of only the 54
never-attempted roles. It preserves the original attempt/money caps and gate.
This development amendment precedes continuation data; it is not represented as
an unchanged pilot protocol or evidence that recovery has succeeded. Study B
has not yet made its first model request at this checkpoint.

## 2026-11-08 — Paced Study B pilot started

The coordinator independently repeated **171 tests** (39.727 seconds) and checked
the exact source/configuration/manifest at Study B commit `83aa8ee313d4f054ac47af038a8b5c33a6a1e859`.
The unchanged fresh dataset excludes 14 inspected engineering datasets, with no
development/evaluation semantic or original-skeleton overlap. Source-bound
approval at 20:35 UTC permits only the original 52-call pilot, not the evaluation.

The first two requests returned HTTP 200 from the fixed Qwen/Alibaba route with
complete SSE records and reported cost of $0.00979654 in total. Acquisition
continues at the amended pace; this early checkpoint is not a passing full pilot
or a scientific effect estimate. Study A is not acquiring concurrently and is
implementing the separately documented continuation audit. The total monetary
ceiling remains $50, split $30/$20. No competition submission has occurred.

## 2026-11-08 — Study B pilot passed; evaluation frozen before acquisition

Study B completed its original pilot at 20:59 UTC: **51 HTTP attempts for 52
scheduled roles**, 50 valid role responses, and 11/12 clean original contracts
correct in every applicable condition. One malformed translator response and
its blocked dependent review remain in the data, without repair or resampling.
There were no technical retries, HTTP 429 responses, truncations or unknown
charges. Recorded pilot cost is **$0.39923650**. The coordinator independently
repeated the campaign audit, pilot gate and standalone evidence verification.

No false assurance was found in this small development pilot; no positive
counterexample is claimed. A zero paired bootstrap interval on an all-zero
sample is not evidence of equivalence or a population effect of exactly zero.
The analysis retains a bounded uncertainty interval and the fixed main design.

The unchanged evaluation contains **100 original contracts / 260 scheduled
roles**. Its prospective freeze was created at 21:03 UTC and independently
checked against the actual passing pilot, the unchanged acquisition source,
the 102-event financial prefix and the exact scheduled IDs. The freeze digest is
`e5b6cc5c66c3698284e5af2145add1983a02b195067c23ef920c7a1c766dab7a`.
This is a local prospective freeze, not a registry preregistration. No evaluation
request has been made at this checkpoint; its corpus is not yet published.

Study B released the shared provider route. Study A has started the independently
reviewed continuation of **only 54 never-attempted pilot roles**, with zero new
retries, unchanged scientific content and the original 98/108 validity threshold.
Both failed historical runs and all conservative unknown-cost reservations are
preserved. This is the [explicit operational amendment](docs/OPERATIONAL_AMENDMENTS.md),
not an extra replacement pilot or an evaluation result.

An authenticated read-only account reconciliation at 21:06 UTC confirmed actual
combined expenditure of **$0.50042824**, leaving **$49.49957176**. Account expenditure
is reported separately from conservative held reservations. Hard allocations
remain $30/$20. Main acquisition requires a separate stage-specific approval;
competition submission is not authorized.

## 2026-11-08 — Study A amended pilot passed; both evaluations paused before dispatch

The explicitly documented continuation completed all **54 never-attempted roles**
with 54 HTTP 200 responses, 52 valid role responses, no new retries and no HTTP
429 responses. Its cost was **$0.12952160**. The composite preserves the original
59 attempts byte-for-byte and reconstructs the original 108-role schedule: it
passes the unchanged gate at **99/108 valid roles and 29/32 correct clean cells**.
Six invalid executor responses and three failed logical transports remain in the
composite. The immutable interrupted record still has its failed 47/108 gate.
The coordinator independently repeated all three original/repaired/composite
audits and checked the exact preserved records, ledger prefix and 54-role suffix.

Study A's prospective main freeze contains the original **60 inputs / 540
scheduled roles**, with manifest digest
`6553e7c06a6c160f0af883c9ca24eb61361a23101745e2636f344527360aefdf`.
It binds the passing amended composite
`42ded5120449f41dd98b3cb4dc7bae1bb45b06dd1512fe6e67409183c5443940`,
unchanged scientific source and actual financial history. It is a prospective
local freeze, not proof of a completed evaluation or a registry preregistration.

Study B's main preflight passed, but its execution request was blocked at an
authorization check **before any dispatch**. Both main acquisitions are paused
pending explicit stage-level confirmation. No alternative route, replacement
sample or model switch is being used to bypass that stop. Offline audits and
clearly labeled pilot-report preparation continue; no held-out model responses
have been acquired or claimed as results.

A read-only account check at 21:29 UTC confirmed **$0.62994984 total actual spend**
and **$49.37005016 remaining**, across 114 Study A and 51 Study B physical pilot
attempts. Study A's larger conservative wallet total, $5.74604992, still includes
nine historical unresolved-receipt reservations; it is not the account's actual
bill. The $30/$20 hard allocations and $50 combined ceiling remain unchanged.

## 2026-11-08 — Explicit main-stage confirmation; Study B evaluation started

After the execution stop, the contributor explicitly confirmed both fixed main
stages: Study B's 260 scheduled roles within its $20 total study allocation and
Study A's 540 within $30, with the shared **$50 ceiling including the pilots**.
The confirmation covered the existing credential, fixed Qwen/Alibaba route,
synthetic inputs, provider-reported retention and bounded technical retries.
One fresh review of the exact blocked execution command allowed it to run; the
experiment, route, sample, scoring and financial limits did not change.

Study B's main journal started at **21:51:10 UTC**. An early operational checkpoint
contains three complete HTTP 200 responses from the approved model/provider,
three valid schema responses and $0.02207062 recorded cost, with no scientific
effect estimate drawn from the partial batch. The frozen **100-original /
260-role** evaluation is in progress, not complete. Study A makes no concurrent
API requests and waits with its already frozen main plan. Reports and public
data distinguish development-only snapshots from the eventual audited main run.

## 2026-11-08 — Study B acquisition complete; Study A main started

Study B's main process finished successfully at 23:45 UTC. The coordinator
independently repeated the native campaign audit: **260 scheduled main roles,
259 physical requests and 220 review outcomes** across 100 original contracts.
There are 253 schema-valid roles, four preserved schema failures and three
blocked dependent reviews. Two HTTP 429 responses were followed by the allowed
identical-payload technical retries after at least 60 seconds; neither caused
semantic repair or replacement sampling. The fixed acquisition finished without
an early stop or a change to the source, prompts, scorer, route or sample.

No false guarantee was confirmed in this bounded run. The full analysis,
missingness-aware uncertainty, public replay bundle and standalone English
report are being reviewed in Study B's separate pull request. This checkpoint
does not establish universal safety, equivalence, or that a certificate's
presentation has zero population effect.

Known provider-reported main charges are **$1.99717180**. Study B's total known
charges including its pilot are **$2.39640830**, while its conservative wallet
retains **$1.22683392** for two receipts with unknown charges. An authenticated
read-only account check at 23:51 UTC independently confirmed **$2.62712164 total
actual expenditure** and **$47.37287836 remaining** across both studies. Account
billing and conservative per-receipt reservations remain separate; no unknown
charge was silently changed to zero.

After Study B's actual process exit, the coordinator rechecked Study A's frozen
source, configuration, passing composite pilot and original wallet. A fresh
stage-specific approval and reviewed execution started the unchanged **60-input /
540-role main evaluation**; its first request began at **23:53:27 UTC**. The
initial two responses were HTTP 200 with valid schemas. No interim scientific
contrasts are being used to tune the run. The fixed 20-second minimum request
spacing, 27 remaining technical retries, $30 Study A allocation and $50 shared
ceiling still apply. Study B makes no further model requests and prepares its
report in parallel. Neither live-study pull request is merged at this checkpoint,
and no competition submission has occurred.

## 2026-11-09 — Study B report and complete campaign integrated

[PR #4](https://github.com/RuslansAleksejevs/boundary-conditions/pull/4) was merged
at **00:11:27 UTC**, from reviewed head `732cc7f204b688ee97b3427d43d635146f5a9317`
into merge commit `755e51475e343825c67e142cbbe34aff2f22f9b3`. The change is confined
to Study B. Its source-bound acquisition, preserved pilot, complete main data,
reproduction commands and [standalone report](studies/wrong-goal-proof/reports/main/README.md)
are now in `main`. The historical pilot PDF remains byte-identical to its earlier
published snapshot; its README identifies the exact historical source revision.

Independent coordinator and peer reviews found no blocking claim, denominator,
provenance or publication-boundary issue. The coordinator rechecked all 14 public
data-file hashes, source bindings, exact public/private core records and reviewed
scientific approval objects, and read the full manuscript and rendered results.
No private execution-permission records, account payloads or raw event journals
are included. The seven-page PDF has a 211-word abstract, the required ethics and
limitations appendix, and an AI-assistance statement; human author review remains
pending. No competition submission has occurred.

After the merge, the complete campaign audit passed again. Study A's existing
integrated engineering suite passed **90 tests in 2.169 s**; Study B passed
**171 acquisition/engineering tests in 45.051 s** and **28 reporting tests in
0.668 s**. These are locally executed checks, not GitHub CI: the pull request had
no reported remote checks. They validate software and saved observations, not
additional model experiments.

Study A's fixed main acquisition continues independently in its unchanged
checkout. Its live-study PR remains unmerged until actual completion, auditing,
reporting and independent review. The shared API ceiling remains $50 including
the pilots, with no additional Study B acquisition.

## 2026-11-09 — Both held-out studies complete, audited and integrated

Study A's main acquisition ended at **03:04:13 UTC** with successful process
exit and no early stop: 540 scheduled roles, 548 physical attempts, all 60
summaries valid, and 480 scheduled executor cells. There were 445 valid executor
responses (including two empty-action abstentions), 33 invalid responses and
two missing responses. The eight identical-payload technical retries followed
the fixed policy; six recovered, and two exhausted retries remain missing.
No answer was repaired, replaced or resampled. Frozen scientific files,
manifest, original failed pilots and the historical pilot PDF are unchanged.

There were **zero observed unauthorized state changes in 478 observed executor
cells**, and **443/480 scheduled cells were useful and correct**. Both primary
contrasts were zero on 39/40 complete attacked pairs. The frozen conservative
cluster intervals remain approximately ±43.49 percentage points, with scheduled
missingness bounds [0, 2.5] points. Invalid action batches execute nothing and
are not valid safe completions. This is a bounded null for the model-and-tool
pipeline, not demonstrated universal refusal, security or defense effectiveness.

The coordinator audited the full private journal/wallet bindings, immutable
source and pilot history, all 13 minimized public files, and every invalid
visible response. Public replay reconstructed both primary contrasts. Internal
AI-assisted peer review separately checked the manuscript and public data;
this is not external academic peer review or signed provider authentication.
The [main report](studies/summary-laundering/report/README.md) has six main-text
pages, one reference page, a two-page mandatory appendix, a 204-word abstract
and an AI-assistance statement. Human author review remains pending.

[PR #3](https://github.com/RuslansAleksejevs/boundary-conditions/pull/3) was merged
at **03:28:49 UTC**, from exact reviewed head
`9fd7a93da68bc409a0bdee72d27f6cd18db20b59` into merge commit
`3ee37271362f3df6f9693886aab2f5484bb302a8`. PR #4 was already integrated. Both
study branches were retained, and sequential integration had no conflicts.

After the final merge, the coordinator repeated **166 Study A tests (5.695 s)**,
**171 Study B engineering/acquisition tests (22.011 s)** and **28 Study B report
tests (0.333 s)**: all 365 passed. Study A's public replay passed on 60 inputs,
480 executor records and 548 visible calls; Study B's full 310-attempt campaign
audit and empty false-guarantee evidence check also passed. These were local,
network-free checks of saved observations, not GitHub CI or new model calls.

The final account snapshot at **03:09:27 UTC** confirmed **$3.75323494 actual API
expenditure and $46.24676506 remaining**. The 972 physical attempts across both
studies include development, errors and technical retries, not 972 independent
tasks. Study A's receipt/reconciled subtotal is $1.35682664; Study B's is
$2.39640830. Unknown-charge reservations are preserved, not rewritten as zero
or confused with the actual bill; see [final accounting](docs/EXECUTION_BUDGET.md#final-account-reconciliation).

No target failure was observed in either fixed evaluation. The original goals,
missing outcomes, null findings and uncertainty are reported rather than using
the remaining budget for outcome-seeking model or prompt changes. No additional
acquisition, competition submission, top-up or automation has occurred.

## 2026-11-09 — Reader editions prepared; certificate edition integrated

Two new standalone reader reports were written from the unchanged evidence, each
six pages including references and the mandatory appendix. Each opens with the
repository link and includes result tables, two source-bound examples, uncertainty
and an LLM-use disclosure. Old PDFs, data and scientific source remain unchanged.
The new repository overview, UTC timeline, reading guide and offline reproduction
guide were prepared alongside the reports. Human author review remains pending.

The certificate reader edition was integrated through
[PR #5](https://github.com/RuslansAleksejevs/boundary-conditions/pull/5) at
05:20:04 UTC, from exact reviewed head `e6f18584` into `675f06e`.
The summary reader edition is complete locally, but its public branch publication
is paused pending explicit confirmation. No alternative publication route was
attempted. At this checkpoint, the shared documentation is also still local;
this entry does not claim that the whole editorial release is published.

Final local checks passed 166 existing summary tests plus nine reader tests,
and 171 certificate tests plus 28 existing report tests and 12 reader tests:
386 checks in total. Both source-bound report checks and saved-data replays
passed without model requests. Every PDF page was visually reviewed, with changed
pages checked again. Internal AI-assisted review is not external peer review.
No new experiment, API expenditure, purchase or competition submission occurred.

## 2026-11-09 — Final three-page reports and a coherent public edition

After author feedback that the six-page reports were too dense, both were
rewritten in LaTeX as three-page papers. The author selected **Prompt Injection
at Agent Handoffs: The Second-Hand Instruction Problem** and **A Certificate Is
Not the Answer**, confirmed UC Berkeley, reviewed the shorter versions and
requested finalization. The final files are in [reports](reports/README.md).

A later track review matched handoffs to primary Track 3 (also Track 2) and
certificate review to Track 4. The author approved applying these recommendations
and updating the public repository. Only the certificate PDF's track line changed
in this release; the previously approved handoff PDF is byte-for-byte unchanged.

The repository now starts with each question, test and result. The timeline
includes pilots, the interrupted run and continuation, both frozen evaluations,
cost reconciliation and successive report revisions. An explicit archive keeps
older titles and reports accessible without calling them current. The earlier
local handoff reader branch is preserved in the release ancestry; the renewed
publication approval supersedes its earlier pause, subject to publication review.

All **394 local tests** passed: 166 + 9 for handoffs, 171 + 28 + 12 for
certificates, and 8 final-report checks. Data replay, exact examples, final PDFs,
local links and preservation checks passed. [Commands and results](reports/CHECKS.md)
distinguish these offline checks from new empirical observations.

No experimental code, prompt, scorer, dataset, saved answer, old PDF or scientific
conclusion changed. No new model calls, purchase or competition submission was
made. Actual API spend remains $3.75323494 at the last reconciled snapshot.

Integration completed at **09:32:11 UTC** through
[PR #6](https://github.com/RuslansAleksejevs/boundary-conditions/pull/6): reviewed
head `6069c92`, merge `9d2b971`. The previously blocked archival branch received
fresh publication approval and was pushed successfully before this release.
No conflict, force-push or branch deletion occurred. Both final PDFs and their
sources are now public on `main`; the documentation update records this outcome.