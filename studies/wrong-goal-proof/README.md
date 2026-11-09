# Verified, but What?

A correct certificate can prove the wrong task. Can a model reviewer tell the difference?

[Read the new report](reports/reader/verified-but-what.pdf) ·
[Explore the data](results/live-main-2026-11-08/README.md) ·
[Check the examples offline](reports/reader/README.md)

## The result, first

The tested model **did not mistake a planted substitution for a correct original
answer**. Qwen3.5-122B-A10B, through the fixed Alibaba route, correctly handled
every planted fault and every equivalent rewrite under all three certificate
presentations. The main evaluation used 100 original contracts.

| Held-out tasks | Useful correct answers | What remains uncertain |
| --- | --- | --- |
| Natural translation and review | 36/40 | Three malformed translations and one malformed review remain unassessed. |
| Planted changes with valid local proofs | 40/40 in each presentation | These are deliberately injected faults, not natural model errors. |
| Harmless equivalent rewrites | 20/20 in each presentation | These reuse the same originals across presentations. |

The primary and secondary paired differences were both zero on 40 complete pairs.
Their conservative 95% intervals still span approximately **−42.95 to +42.95
percentage points**, assuming independent originals. Shared templates limit that
assumption. This is a bounded negative result—not proof of general safety,
presentation equivalence or a benefit from scope warnings.

## The boundary we tested

The original contract says which Boolean states are allowed and what must hold in
them. A translator proposes a candidate. Exact local code checks the candidate;
a fresh model reviewer must answer the **original** task.

For fixed candidates, the reviewer sees the same evidence under three headings:
ordinary **PASS**, neutral **verification record**, or explicit **candidate-only
scope**. Every condition sees the original task and an instruction to check the
match. The scoped condition gets no hidden answer.

One real case reversed an implication. The altered claim had a valid exhaustive
SAFE certificate, but the original was false when all four inputs were false.
The model returned that exact counterexample, even with the PASS heading.
The report pairs it with a harmless rewrite, `q` → `q AND q`, which the model
correctly accepted. [Exact records and checks](reports/reader/README.md#two-source-bound-examples)
make both examples inspectable.

## Read, inspect, reproduce

- **[Reader report](reports/reader/verified-but-what.pdf):** a fresh, standalone
  explanation with result tables, real examples and explicit limits. Pending
  human author review; not submitted to the competition.
- **[Public campaign](results/live-main-2026-11-08/README.md):** frozen inputs,
  prompts, visible answers, certificates and analyses. Development and main
  results remain separate.
- **[Report guide](reports/README.md):** the new edition and unchanged historical
  pilot/main PDFs, with build and audit instructions.
- **[Engineering guide](ENGINEERING_GUIDE.md):** language, adapters, software
  rehearsals and commands. Test doubles are never model observations.

From the repository root, with Python 3.11+ (tested on 3.14.6):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 studies/wrong-goal-proof/reports/reader/check_report.py
```

This makes **no model calls**. It rechecks saved observations, mathematical
examples, table values and preserved files. No API key or third-party Python
package is needed. Hashes check local consistency, not signed provider origin.

The study's known pilot-plus-main API cost is USD2.39640830; two unknown charges
retain conservative holds. [Exact accounting](reports/main/README.md#requests-failures-and-cost)
distinguishes recorded costs from reservations. Research-assistant usage is separate.

## Research record

[Historical plan](PLAN.md) · [Design decisions](DESIGN.md) ·
[Software validation](VALIDATION.md) · [Live protocol](LIVE.md) ·
[Current state](STATE.md) · [Append-only history](HISTORY.md)

The study is confined to synthetic four-input contracts. It does not offer a
general definition of mathematical equivalence or a production security claim.
No license has been selected; public visibility alone is not an open-source license.