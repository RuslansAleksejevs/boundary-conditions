# Study state

As of 8 November 2026 UTC. Implementation evidence: local code and CPU tests.
Research effects: UNKNOWN, not measured with an LLM.

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
  findings fixed with regression tests. Publication is in progress, not integrated
  into main.

Next: publish the study branch/PR for coordinator integration. A separate
authorized model interface and bounded budget are the minimum
external requirements before a real pilot; do not weaken the policy to obtain an effect.