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