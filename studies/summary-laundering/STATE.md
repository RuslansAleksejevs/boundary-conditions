# Study state

As of 8 November 2026 UTC. Implementation evidence: local code and CPU tests.
Research effects: UNKNOWN, not measured with an LLM.

## Current continuation

The offline implementation was integrated through PR #1. A new authorized stage
is in preparation on `study/summary-laundering-live-v1`, based on main `afd055c`.
Batch spending is authorized within a separate study ceiling of USD 30; model
access and exact coordinator preflight remain prerequisites. No credential
attachment attempt or model request has been made by this workstream.

Implemented an initial official HTTPS adapter, durable conservative wallet,
fresh-case generation, frozen schedule, distinct live audit and real pilot gate.
The existing offline-only manifest checks remain intact. The current suite is
**123/123 PASS** (2.281 seconds), entirely local and HTTP-free. Read-only review
identified two receipt-integrity gaps: trusting a logged retry flag and accepting
duplicate/empty provider IDs. Both are fixed and regression-tested; the peer
confirmed the fixes against exact file hashes. This is code review, not provider
or empirical approval. See LIVE_PROTOCOL.md and VALIDATION.md.
Final model/sampling/pricing parameters and approved credential access remain
pending. Actual model requests and experimental spend in this stage: **0**.

Prepared code is published in [draft pull request #3](https://github.com/RuslansAleksejevs/boundary-conditions/pull/3),
implementation commit `4030c75c16f88b4add9e652073e8ba0216344d34`.
It is not integrated into main. The draft records an access-blocked preparatory
milestone, not completion of the empirical research goal.

Next: obtain the exact preflight GO and approved secret availability, then
execute the actual bounded pilot and main
evaluation if gates pass. Do not mistake these preparatory tests for completion
of the newly authorized scientific stage.

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