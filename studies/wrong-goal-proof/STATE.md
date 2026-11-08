# Study state

As of 2026-11-08 UTC. Source: implementation and local test commands;
classification: PROJECT_REPORTED. This is an engineering record, not model evidence.

- Implemented a self-contained Python/stdlib Boolean-contract testbed, independent
  scalar/vector semantics, exhaustive certificates, seeded disjoint datasets,
  natural translation and paired certificate replay, offline adapters, manifest,
  incremental logging, freeze rehearsal, audit, and paired analysis.
- Latest complete test pass: 146 tests, Python 3.14.6, 20.539 seconds. This includes
  the original 105 tests plus 41 live-interface/exclusion/ledger tests.
- No experimental model calls, paid batches, or competition submission.
- A separate live HTTP interface, persistent USD20 wallet, source/configuration/
  manifest-bound GO, actual-pilot freeze and campaign auditor are implemented.
  Acquisition is blocked by unavailable approved credential access and the final
  provider/settings/pricing/data-policy preflight. Offline replay does not attest
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

Next: coordinator review of the published live preparation, then resolve
credential availability and the exact source-bound acquisition GO. No real model
pilot, empirical freeze, main evaluation or empirical report/PDF exists yet.

## Next stage — live preparation, 8 November 2026 UTC

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
