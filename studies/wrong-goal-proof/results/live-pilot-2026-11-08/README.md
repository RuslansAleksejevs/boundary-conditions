# Actual development pilot — not a full campaign export

Real Qwen3.5-122B-A10B / Alibaba observations acquired 8 November 2026. The
20-original pilot used 51 actual requests for 52 scheduled roles. The gate passed
at 50/52 schema-valid roles and 11/12 clean originals correct. Main had not started
when this immutable view was exported; later acquisition status is in [STATE.md](../../STATE.md).
See the [pilot report](../../reports/pilot/README.md) for results and limitations.

This directory preserves exact visible pilot records and a clearly labeled
development-only subset. It is intentionally **not** a valid complete dataset for
`run_live.py audit-campaign`. The 100 held-out task records and engineering-exclusion
corpus are withheld until main acquisition ends. Manifest/freeze hashes and schedule
metadata are not the held-out task contents or an empirical main result.

| File | Scope |
| --- | --- |
| `development-cases.json` | Exactly 20 original dev case objects, wrapped as a subset with the complete source dataset hash; not relabeled as the original dataset. |
| `run.json` | Exact 52 logical roles, 44 reviewer outcomes, 51 visible HTTP receipts and the preserved invalid/blocked roles. No hidden reasoning text. |
| `analysis.json` | Exact actual-pilot aggregate analysis, usage, missingness, utility, family breakdowns and uncertainty. |
| `evidence.json` | Actual false-guarantee packet: 0 cases/0 claims, independently verifiable. |
| `manifest.json`, `freeze.json` | Exact prospective scientific configuration and post-pilot freeze bindings. No main answers. |
| `audit.json`, `gate.json` | Results of the full audit/gate against the private complete corpus before export. |
| `budget.jsonl` | Exact 102-event pilot-only ledger; USD 0.39923650, no unknown charges. |
| `EXPORT.json` | Byte/canonical hashes and explicit public verification limits. |

The purpose-written scientific pilot authorization reference and opaque provider
generation IDs are retained for consistency. They are not credentials, private
coordination messages or provider signatures. Raw event journals, account
responses, personal host paths and secrets are not included.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 studies/wrong-goal-proof/reports/pilot_release.py verify --view studies/wrong-goal-proof/results/live-pilot-2026-11-08
```

This credential-free check verifies the file inventory, pilot request/answer
mathematics, 52 logical roles, 44 outcomes, aggregate analysis, zero actual false
guarantees and internal source bindings. It repeats physical-receipt usage sums
separately from scheduled-role counts. It does **not** reproduce the complete
live acquisition or dev/holdout separation audit without the withheld corpus;
the saved full audit remains a project-reported result. Hashes do not authenticate
provider origin, establish public preregistration or replace human review.