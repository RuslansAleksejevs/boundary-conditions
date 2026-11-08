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