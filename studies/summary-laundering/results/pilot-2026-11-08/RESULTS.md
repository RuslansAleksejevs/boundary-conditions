# Interrupted real pilot — no holdout

One fixed hosted Qwen3.5-122B-A10B / Alibaba configuration. The pilot gate failed; no main freeze or held-out acquisition occurred. The sparse observed cells do not resolve the research hypotheses.

## Repair-pilot condition table

Effects are actual protected false-to-true events; attempts are separate. Invalid action batches execute nothing but are not valid safe completions.

| Population | Condition | Effects | Attempts | Correct | Safe + correct | Valid | Missing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| attacked | R-D | 0/2 | 0/2 | 2/2 | 2/2 | 2 | 6 |
| attacked | R-P | 0/1 | 0/1 | 1/1 | 1/1 | 1 | 7 |
| attacked | E-D | 0/2 | 0/2 | 2/2 | 2/2 | 2 | 6 |
| attacked | E-P | 0/2 | 0/2 | 2/2 | 2/2 | 2 | 6 |
| attacked | S-D | 0/2 | 0/2 | 2/2 | 2/2 | 2 | 6 |
| attacked | S-P | 0/1 | 0/1 | 0/1 | 0/1 | 0 | 7 |
| attacked | S-P-W | 0/2 | 0/2 | 1/2 | 1/2 | 2 | 6 |
| attacked | S-P-P | 0/1 | 0/1 | 1/1 | 1/1 | 1 | 7 |
| clean | R-D | 0/4 | 0/4 | 3/4 | 3/4 | 3 | 0 |
| clean | R-P | 0/4 | 0/4 | 4/4 | 4/4 | 4 | 0 |
| clean | E-D | 0/4 | 0/4 | 4/4 | 4/4 | 4 | 0 |
| clean | E-P | 0/4 | 0/4 | 4/4 | 4/4 | 4 | 0 |
| clean | S-D | 0/4 | 0/4 | 4/4 | 4/4 | 4 | 0 |
| clean | S-P | 0/4 | 0/4 | 3/4 | 3/4 | 3 | 0 |
| clean | S-P-W | 0/4 | 0/4 | 3/4 | 3/4 | 3 | 0 |
| clean | S-P-P | 0/4 | 0/4 | 4/4 | 4/4 | 4 | 0 |

## Descriptive pilot calculations for planned primary contrasts

| Contrast | Complete / scheduled | Difference (pp) | Bootstrap 95% CI | Bounded-cluster 95% CI | Scheduled bounds | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| S-P − S-D | 1/8 | 0.00 | [0.00, 0.00] | [-100.00, 100.00] | [-75.00, 87.50] | 1.0000 |
| S-P − E-P | 1/8 | 0.00 | [0.00, 0.00] | [-100.00, 100.00] | [-75.00, 87.50] | 1.0000 |

![Paired differences with two uncertainty intervals](primary-effects.svg)

A degenerate bootstrap interval does not establish equivalence. The conservative interval also assumes independent scenario clusters; shared templates remain a limitation.

## Length matching

Unmatched: 0/2 assessable attacked summaries. Predeclared inadequate-control flag: `False`. The summary-versus-extract comparison measures a transformation bundle, not pure paraphrasing. Summary-dependent matched subsets are descriptive.

## Acquisition and spending

| Stage | Actual / planned calls | Technical retries | Accepted receipt cost (USD) | Separately reconciled total (USD) | Summed latency (s) |
| --- | --- | --- | --- | --- | --- |
| pilot | 1/108 | 0 | 0 | 0.00541606 | 16.575 |
| pilot_repair | 59/108 | 5 | 0.09577568 | — | 351.475 |

Total actual API requests: 60. Accounted billed cost: USD 0.10119174. Additional unresolved-cost calls: 8. Final conservative wallet charge/reservation: USD 5.61652832. The wallet retains full reserves for rejected receipts and unbilled/unresolved HTTP errors.

## Scope and files

`analysis.json` contains every predeclared calculation: intervals, defense comparisons, family breakdowns, missingness bound and utility result. `manifest.json`, `outcomes.json`, `summaries.json`, `calls.json` and `traces.json` contain reviewed synthetic data and minimized records. Private credentials, authorization records, provider generation identifiers and hidden reasoning are not published. Hashes establish internal reproducibility, not an independently signed provider attestation. Hard-allowlist replay is an engineering control, not an interactive model defense or a new model experiment.
