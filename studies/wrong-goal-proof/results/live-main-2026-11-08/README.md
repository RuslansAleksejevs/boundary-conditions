# Complete real-model campaign — 8 November 2026

This is the reviewed synthetic-task export of the actual Qwen3.5-122B-A10B /
Alibaba development pilot and frozen main evaluation. It is not a test-double
run, external replication, provider-signed record or public preregistration.
The source main ended before export; no held-out corpus was released mid-run.

Main: 100 originals, 260 scheduled roles, 220 reviewer outcomes, 259 physical
requests. Pilot: 20 originals, 52 roles, 44 outcomes, 51 physical requests.
There were zero observed false guarantees in either stage. Main B/N/S each
correctly answered 40/40 planted originals and 20/20 equivalent controls; natural
useful completion was 36/40 with 0/37 drift among valid translations. Read the
[standalone report and limitations](../../reports/main/README.md) before interpreting
these counts. The empirical null does not establish presentation equivalence or
general safety.

`EXPORT.json` inventories the exact 14 exported data/audit files with byte hashes
and, where applicable, canonical digests. The complete dataset, manifest, freeze,
unchanged hash-chained wallet, both visible runs, analyses, evidence packets and
audits are included. Main and pilot failures remain intact. Both empty evidence
packets mean zero observed false guarantees, not missing invented examples.

The exporter reran the unchanged native campaign auditor on the copied records:
PASS, 310 physical attempts, no new API calls. Known campaign cost is USD2.39640830
for 308 attempts; two HTTP429 charges are unknown. Their USD1.22683392 full holds remain,
for a cumulative conservative commitment of USD3.62324222. This is not an exact
bill. Account records, private raw journals, credentials, hidden reasoning text,
host paths and private coordination/permission messages are not exported.
Opaque technical provider generation IDs remain for receipt consistency; they
are not credentials. The exact purpose-written scientific GO objects were
separately reviewed and preserved unchanged, not replaced with later private
execution-permission records.

From the repository root, without credentials or network:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 studies/wrong-goal-proof/run_live.py audit-campaign --campaign studies/wrong-goal-proof/results/live-main-2026-11-08
PYTHONDONTWRITEBYTECODE=1 python3 studies/wrong-goal-proof/run_live.py verify-evidence --evidence studies/wrong-goal-proof/results/live-main-2026-11-08/main/evidence.json
PYTHONDONTWRITEBYTECODE=1 python3 studies/wrong-goal-proof/run_live.py verify-evidence --evidence studies/wrong-goal-proof/results/live-main-2026-11-08/pilot-v1/evidence.json
```

Audit `new_model_calls=310` counts the historical acquisition, not requests sent
by these audit commands. All reproduce only saved observations. Additional
reporting commands and exact denominators are in the linked report. No more model
acquisition or competition submission is authorized by this release.