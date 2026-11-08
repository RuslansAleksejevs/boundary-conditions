# Study state

As of 8 November 2026 UTC. Implementation evidence: local code and CPU tests.
Research effects: UNKNOWN; the first real pilot stopped on an interface error.

## Current continuation

The offline implementation was integrated through PR #1. A new authorized stage
is underway on `study/summary-laundering-live-v1`, based on main `afd055c`.
Batch spending is authorized within a separate study ceiling of USD 30. Approved
credential access and exact source/configuration-bound preflight were obtained.

Implemented an initial official HTTPS adapter, durable conservative wallet,
fresh-case generation, frozen schedule, distinct live audit and real pilot gate.
The existing offline-only manifest checks remain intact. The current suite is
**133/133 PASS** (1.957 seconds), entirely local and HTTP-free. Read-only review
identified two receipt-integrity gaps: trusting a logged retry flag and accepting
duplicate/empty provider IDs. Both are fixed and regression-tested; the peer
confirmed the fixes against exact file hashes. This is code review, not provider
or empirical approval. See LIVE_PROTOCOL.md and VALIDATION.md.
The user renewed execution authority and selected Qwen3.5-122B-A10B through
OpenRouter/Alibaba before any observations. Approved secret access is now reported
available. The old gpt-oss fixture is superseded, without model search or observed
effects. The fixed Qwen-compatible SSE configuration reserves full native context
for both input and billed output, with the hard USD 30 wallet unchanged.
The coordinator independently reported 133 tests passing (1.897 seconds), and
the peer confirmed the final billing/context fixes against exact file hashes.

At 20:11:55 UTC, the first real pilot began under commit `02e34e6`. It stopped
after **one** planned clean-summary request: HTTP 200, correct model/provider,
16.575 seconds, terminal DONE, but the provider repeated an empty `stop` chunk
with final usage. The strict SSE assembler rejected this repeated finish marker.
No executor or attack request was sent. The immutable run audit passed; the
pilot gate failed (0/108 usable role responses, all 96 executor cells missing).
The received usage reported 231 prompt and 2,575 completion tokens, including
2,531 reasoning tokens, and USD 0.00541606. Because the receipt was rejected,
the wallet retains the full **USD 0.61341696** reservation. An independent
read-only account reconciliation confirmed USD 0.00541606 actually billed.
This is not a scientific null result. The coordinator approved the sole narrow
interface correction and one fresh repair pilot. The correction passes
**135/135 tests in 1.735 seconds**, including the sanitized observed terminal
pair and malformed variants. A read-only replay of the complete saved 14-event
stream also passes; the original run remains failed and unchanged. The renewed
exact-source GO is still required; no repeat is running.

Prepared code is published in [draft pull request #3](https://github.com/RuslansAleksejevs/boundary-conditions/pull/3),
initial preparation commit `4030c75c16f88b4add9e652073e8ba0216344d34`.
It is not integrated into main. The draft records implementation and subsequent
live-stage progress, not completion of the empirical research goal.

Next: resolve the exact terminal-usage SSE compatibility issue under a renewed
source-bound GO, using the sole allowed fresh interface-repair pilot. Preserve
the failed pilot and its financial hold. Main evaluation still requires a
passing real pilot, an audit and a measured cost/time checkpoint.

## Previous offline milestone

- Self-contained stdlib harness, strict action/event scorer, eight replay cells,
  allowlist replay, deterministic generators, immutable output directories,
  audited manifests/logs and paired analysis are implemented.
- Final suite: **90/90 tests PASS**, Python 3.14.6. Eight saved CLI runs passed
  audit: seven 12-input development rehearsals and one 60-input engineering
  validation. Exact commands and counts are in VALIDATION.md.
- Method amendments precede all model observations; see METHOD_CHANGES.md.
- Real pilot, empirical freeze, holdout, and competition submission: NOT RUN.
- Approved experimental model interface, price and batch authorization: NOT
  ESTABLISHED. No network/model batch was attempted; external API requests: 0.
- Read-only peer review completed; manifest/profile and usage/cost integrity
  findings fixed with regression tests.
- Published branch: `study/summary-laundering`.
  [Pull request #1](https://github.com/RuslansAleksejevs/boundary-conditions/pull/1)
  was merged by the coordinator as `9a01ded`; this workstream did not merge it.
  Implementation commit: `5bf037c1c0587510c69740f267ca3f8f76041cd1`.

The original offline stage is complete. Do not weaken the policy to obtain an effect.