# Read the result

Start with **[Verified, but What? — reader edition](reader/verified-but-what.pdf)**.
It explains the question, the completed experiment, the null result and two real
handoffs in plain English. The original task stayed visible; the model correctly
handled all planted faults in this setting.

The new report was written afresh from the frozen evidence. It adds no model
observations and changes no outcome, method or interval. It remains pending
human author review, not a competition submission.

## Choose a level of detail

| Document | What it is for |
| --- | --- |
| [Reader PDF](reader/verified-but-what.pdf) / [source and checks](reader/README.md) | The question, results, examples and limits. Start here. |
| [Historical main report](main/README.md) / [PDF](main/main-report.pdf) | The original completed-main manuscript, full accounting and operational detail. Preserved unchanged. |
| [Historical pilot report](pilot/README.md) / [PDF](pilot/report.pdf) | The development-only checkpoint, before main acquisition. Preserved unchanged; not the current result. |
| [Complete public data](../results/live-main-2026-11-08/README.md) | Both saved stages, the frozen dataset, certificates, manifest and replayable analysis. |

## Reproduce without a model

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 studies/wrong-goal-proof/reports/reader/check_report.py
```

The [reader guide](reader/README.md) gives the full test and cached-PDF build
commands, exact source map, selection rule and check scope. It distinguishes
historical API attempts from the **zero new requests** made by replay.

[Reporting tools](TOOLS.md) preserve the detailed export, chart, pilot-release
and accounting documentation. [Sources](SOURCES.md) record the official template
and related-work reading scope; the reader guide notes the latest recheck.