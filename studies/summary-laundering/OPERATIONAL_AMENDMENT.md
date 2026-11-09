# Prospective operational continuation amendment

Recorded 8 November 2026 after a development outage and **before any continuation
request**. This is not an unchanged preregistered pilot, a replacement sample, or
permission to relax a scientific gate. Execution still requires a separate
source-bound coordinator GO and exclusive use of the experimental provider route.

## Observation and decision

The original pilot stopped after one clean-only response because its SSE parser
rejected an idempotent terminal usage footer. The one allowed interface repair
was made and tested. The fresh repaired pilot then made 59 attempts for 54
distinct logical requests: 51 complete provider responses, eight HTTP 429 errors,
and five identical technical retries. Three consecutive failed logical transports
triggered its predeclared circuit. Its original gate remains failed: 47/108 valid
role responses; clean correctness is 29/32. The exact cause of HTTP 429 is unknown.
Public provider health and an account balance cannot establish that rate limits
have been resolved.

An explicit operational amendment permits preparation of **one** append-only
continuation of the exact never-attempted suffix, not another pilot. There are
54 remaining logical requests: six summaries and 48 executor calls over six
wholly untouched inputs. No attempted response—completed, invalid, refused,
truncated or transport-failed—can be sampled again. Existing three failed logical
transports, four invalid batches, summaries, outcomes and all original records
remain unchanged. No attack-effect contrast was inspected to make this decision.

## Unchanged constraints

- The 12 original repair-pilot inputs, schedule, saved-summary identities,
  model/configuration, policy, prompt, generator, state scorer and statistical
  metric functions remain byte-identical or bound to their original bytes.
- There are **zero additional repair-pilot retries**. The original five are
  spent. Combined repair acquisition is at most 59 + 54 = **113 attempts**.
- The same append-only wallet, USD 30 ceiling, 788 campaign attempts and
  32 campaign technical retries remain binding. Existing nine unknown receipt
  reserves are not reset or released by rewriting the ledger.
- The thresholds remain 98/108 valid role responses and 26/32 correct clean
  cells. Maximum attainable validity is 101/108; at least 51 of the remaining
  54 roles must qualify. The clean denominator and 29 correct cells are fixed.
- The original failed pilot/gate is immutable. A separate composite audit and
  amended gate may qualify main only with a new explicit freeze/GO. Failure of
  that gate does not authorize replacement data or another continuation.

## Operational changes and audit

Use at least 20 seconds between attempt starts, measured with a monotonic clock
and waits of at most 30 seconds. Only one study may use this provider route at a
time. A POSIX total wall timer enforces the existing 180-second request limit;
this closes a slow-drip gap in a per-read socket timeout, not an observed cause
of the rate-limit failure. The three-consecutive-failed-logical-transports circuit
still applies within the continuation.

A new acquisition process also waits 20 seconds before its first attempt, because
it cannot recover the preceding process's monotonic origin. Any later main plan
must explicitly bind the same minimum start spacing and be separately approved.

Before continuation freeze, the operational policy was aligned across studies:
after HTTP 429, wait at least 60 seconds from receipt completion and honor a
longer canonical Retry-After up to 300 seconds. A larger delay halts acquisition
without retry. Only normalized nonnegative decimal seconds are retained; arbitrary
header text and raw provider error bodies are not logged. The cooldown applies
before the next attempt even when it is a different logical role and no retries
remain. It never creates a new retry allowance. Both continuation and future main
manifests bind this policy, and their audits verify recorded monotonic spacing.

The new plan binds the original manifest, complete parent-run hash, parent ledger
prefix, exact remaining role IDs/order, old and amended source inventories, and
limits. A single distinct ledger stage and new output directory record new calls.
The union audit checks immutable prior calls/outcomes, disjoint new first attempts,
the unchanged full schedule, new source-bound authorization, pacing, financial
chain, state reset, replay identity, all missing cells and combined attempt caps.
No record is relabeled to conceal the outage or amendment. A composite record is
clearly distinct from both the original failed run and a fresh experimental run.

Read-only account reconciliation at 20:27:13 UTC reported USD 0.10119174 billed
across the first 60 attempts, exactly the accepted receipts plus the first request.
The eight HTTP 429 responses added no charge in that snapshot. The local wallet
nevertheless retains USD 5.61652832 in charges/reservations. This reconciliation
is financial evidence, not authorization to overwrite uncertainty in old receipts.