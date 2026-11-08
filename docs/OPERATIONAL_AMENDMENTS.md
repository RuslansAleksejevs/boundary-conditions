# Operational amendment: provider throttling

8 November 2026, after development acquisition and **before any held-out
evaluation or continuation**. This is an explicit amendment to the execution
stop rule, not an unchanged preregistered pilot or a new statistical sample.

## What happened

Study A's first planned clean request returned a complete Qwen/Alibaba response,
but the strict SSE parser rejected the provider's repeated empty terminal chunk
carrying final usage. The failed run was retained. The one permitted interface
correction accepts only that identical terminal repetition, with complete billing;
it does not accept changed answers, identities, or finish reasons.

The fresh repaired pilot then made **59 attempts for 54 distinct scheduled
roles**, including its five permitted identical technical retries. There were
51 completed transports and eight HTTP 429 responses. Three consecutive failed
logical requests triggered the declared stop. The audit passed; the full-pilot
gate did not: **47/108 valid roles**. Clean execution was **29/32 correct**, above
the unchanged 26/32 threshold. The remaining 54 roles were never attempted.

An authenticated read-only account check at 20:27 UTC confirmed total spending
of **$0.10119174**, including the first failed-interface request, and a remaining
balance of **$49.89880826**. The monetary cap was not exhausted. The exact source
of the HTTP 429 throttling is unknown; public endpoint health is not proof of
available request capacity. Conservatively held unknown-cost reservations remain
in the study wallet despite account-level cost reconciliation.

## Changes decided before further acquisition

- Serialize the shared provider route: only one study acquires at a time.
- Space HTTP attempt starts by at least 20 seconds. This is a conservative
  operating choice, not a verified provider rate limit or a promise of recovery.
- Where an already permitted technical retry remains, wait at least 60 seconds
  after HTTP 429 and honor a longer valid `Retry-After`. A value above 300 seconds
  stops the stage rather than causing an early retry. No extra retries are added.
- Retain the 180-second request deadline; strengthen Study A's implementation to
  a total wall-clock timer. No actual deadline violation was observed.

Study B receives these transport-only changes **before its first model request**,
with a newly source-bound manifest and approval. Its original unused preparation
is preserved; this is not a repeated pilot.

## Study A: one explicit, auditable continuation

The approved implementation may continue **only the exact 54 never-attempted
roles**, the frozen suffix comprising six untouched attacked inputs. It may not
resample any prior answer, invalid response, or attempted transport failure.
The model, sampling, task data, condition order, prompts, scorer, and scientific
metrics remain unchanged. The original failed runs and gates remain immutable.

A separately named continuation must bind the original manifest, run, ledger
prefix, remaining IDs, and old/new source inventories. It appends to the same
wallet. It gets **zero additional retries**: the repaired pilot's allowance is
already used. At most 59 + 54 = **113 attempts** can belong to the repaired pilot
and continuation together, exactly its original attempt ceiling. The $30 study
cap and 788-attempt campaign ceiling do not increase; Study B retains $20/379.

A separate composite audit may replace only never-attempted missing placeholders
with new observations. It must preserve every previously attempted role and its
receipts, reconstruct the original 108-role schedule, and expose the interruption
and changed acquisition timing. This is not erasure or relabeling of the failed
pilot. The maximum possible composite validity is **101/108**; advancement still
requires **98/108**, so at most three new roles may be invalid or missing.
The existing clean result stays fixed. A failed gate will not be relaxed.

The decision uses transport/completeness and clean-task checks, not a desired
attack-effect threshold. No attack payload or model setting is tuned. A held-out
evaluation still requires an audited passing composite, a new prospective freeze,
and separate coordinator approval. If those conditions cannot be met, report the
pilot-only evidence and limitations. Competition submission remains separate.