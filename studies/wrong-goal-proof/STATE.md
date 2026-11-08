# Study state

As of 2026-11-08 UTC. Source: implementation and local test commands;
classification: PROJECT_REPORTED. This is an engineering record, not model evidence.

- Implemented a self-contained Python/stdlib Boolean-contract testbed, independent
  scalar/vector semantics, exhaustive certificates, seeded disjoint datasets,
  natural translation and paired certificate replay, offline adapters, manifest,
  incremental logging, freeze rehearsal, audit, and paired analysis.
- Latest complete test pass: 105 tests, Python 3.14.6, 5.611 seconds, including
  the additional integrity and standalone-evidence checks.
- No experimental model calls, paid batches, or competition submission.
- Model acquisition is blocked pending an explicitly authorized interface,
  exact provider/model settings, pricing, and spending cap. No live transport is
  included. Offline replay does not attest external acquisition chronology.
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
- Publication: implementation branch only; PR not yet opened, not integrated.

Next: review the synthetic result files, publish the study branch and open a pull
request. A real model pilot and confirmatory holdout remain separately blocked.
