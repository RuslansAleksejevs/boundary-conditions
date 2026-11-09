# Report build

This directory contains presentation tools, separate from the prospectively
frozen acquisition/scoring source. Changing a chart cannot change the saved
model answers, independent certificates, scored outcomes or uncertainty arrays.

`render_figure.py` consumes an already audited `run_live.py analyze` JSON file.
It preserves exact counts and the saved interval estimates and creates a matching
vector SVG and PDF without third-party Python dependencies. It rejects explicitly
offline/test-double modes. This check is not a replacement for the acquisition
auditor: a forged input JSON is not authenticated by rendering it.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s studies/wrong-goal-proof/reports -p 'test_*.py' -q
python3 studies/wrong-goal-proof/reports/render_figure.py --analysis PATH_TO_AUDITED_ANALYSIS.json --out NEW_FIGURE_STEM
```

The presentation tests use fabricated counts clearly marked as fixtures;
they do not contact a model or constitute scientific observations. Output files
are exclusive-create so an earlier figure cannot be silently overwritten. A
development-pilot graphic is explicitly labeled “not confirmatory.” A collapsed
paired bootstrap is shown alongside the conservative bounded-iid interval;
shared generation templates still limit the inference.

After main acquisition has ended, `export_campaign.py` exports only the exact
audited synthetic-task dataset, manifests, freeze, visible stage records,
certificates, accounting and analyses. It refuses a missing main run, scans for
known private-path/credential/coordination patterns, never automatically redacts
or changes an answer, and reruns the unchanged campaign auditor on the exported
copy. Original opaque technical generation IDs are not credentials and remain
available for receipt consistency. Raw append-only event journals and account
records stay private. A manual content review is still required before Git push.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 studies/wrong-goal-proof/reports/export_campaign.py --campaign PRIVATE_COMPLETED_CAMPAIGN --out NEW_PUBLIC_RESULT_DIRECTORY
```

`acquisition_summary.py` also requires an ended main, unchanged source inventory
and passing complete campaign audit. It derives decimal reported-cost subtotals,
unknown-cost/token denominators, separate stage/cumulative wallet commitments,
actual pacing and exact-payload retry pairs. It does not contact the API, repair
records, replace scoring or publish private account reconciliation.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 studies/wrong-goal-proof/reports/acquisition_summary.py --campaign COMPLETED_CAMPAIGN --out NEW_OPERATIONAL_SUMMARY.json
```

Eight additional no-network accounting tests use explicitly invented arithmetic
and timing fixtures; two more replay the already-published pilot metadata. None
are new model observations. UTC receipt gaps and monotonic HTTP/elapsed durations
are distinguished. A completed native audit requires zero unsettled reservations;
unknown settled costs nevertheless retain their full holds.

The five additional publication-boundary tests do not generate new task cases or
contact a provider. They check rejection of unfinished main acquisition and
fictional secret/path/identifier examples, not actual sensitive values.

For the completed development pilot while main is unstarted, `pilot_release.py`
exports only the 20 development originals and exact visible pilot records. It
first audits the complete private source, never releases the 100 held-out task
records, and labels the public subset as something other than the original full
dataset. Public verification rechecks pilot mathematics, aggregate analysis,
physical-receipt usage and hashes. It explicitly does not reproduce the full
acquisition or cross-split separation audit without the withheld corpus.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 studies/wrong-goal-proof/reports/pilot_release.py verify --view studies/wrong-goal-proof/results/live-pilot-2026-11-08
```

Four envelope-boundary tests and five saved-pilot replay/mutation tests cover this
additional publication path. They make no new model calls or observations.
The official report template and source-reading scope are in [SOURCES.md](SOURCES.md).
The [development-only manuscript](pilot/README.md) records the 21:50 UTC pilot
cutoff and remains pending human author review. Its original PDF is preserved;
source-version instructions accompany that historical checkpoint.
The [completed held-out manuscript](main/README.md) and
[complete public campaign](../results/live-main-2026-11-08/README.md) now report
the finished evaluation. Current status is in [STATE.md](../STATE.md).
Neither manuscript has been submitted to the competition.