# Research log

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