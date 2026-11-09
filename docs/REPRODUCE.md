# Check the results offline

You can check the saved observations without an API key, model download or paid
request. Run the commands below from the repository root. The Python programs
use only the standard library; the recorded validation used Python 3.14.6.

This reproduces the analysis of the published responses. It does not generate
fresh responses or independently authenticate what a provider served.

## Start with the final reports

```sh
python3 reports/check_reports.py
python3 -m unittest discover -s reports -p 'test_*.py' -q
python3 docs/check_links.py
```

The first command checks table counts, examples, source structure and file hashes.
It needs no PDF software. Add `--pdf` to also check the compiled layout with
Poppler's `pdfinfo` and `pdftotext`. The link check covers local Markdown file
targets, not external sites or heading anchors.

## Prompt Injection at Agent Handoffs

```sh
python3 studies/summary-laundering/report/check_public.py studies/summary-laundering/results/main-2026-11-09
```

The check rebuilds the mock actions and state changes, then reproduces the two
primary comparisons. A successful result reports:

- `public_replay_passed: true`
- 60 inputs, 480 scheduled executor records, 548 visible call records
- `primary_contrasts_reproduced: 2` and `new_api_requests: 0`

The two missing responses and 33 invalid batches remain in the records. The
check does not repair their text or treat them as correct task completion.

## A Certificate Is Not the Answer

```sh
python3 studies/wrong-goal-proof/run_live.py audit-campaign --campaign studies/wrong-goal-proof/results/live-main-2026-11-08
python3 studies/wrong-goal-proof/run_live.py verify-evidence --evidence studies/wrong-goal-proof/results/live-main-2026-11-08/main/evidence.json
```

The first command checks the saved pilot and main campaign: `valid: true`, with
310 historical HTTP attempts. The field `new_model_calls: 310` in this older
output names the original acquisition count; **the audit sends no requests**.

The second command checks any recorded false guarantees against exact Boolean
counterexamples. Its correct result here is `valid: true` with **zero cases**:
no false guarantee was observed. An empty packet is not a missing positive result.

## Check the implementation

These commands exercise local software fixtures, not the hosted model:

```sh
python3 -m unittest discover -s studies/summary-laundering/tests -q
PYTHONPATH=studies/wrong-goal-proof python3 -m unittest discover -s studies/wrong-goal-proof/tests -q
python3 -m unittest discover -s studies/wrong-goal-proof/reports -p 'test_*.py' -q
python3 -m unittest discover -s studies/summary-laundering/report/reader -p 'test_*.py' -q
python3 -m unittest discover -s studies/wrong-goal-proof/reports/reader -p 'test_*.py' -q
```

The acquisition release passed 166, 171 and 28 tests respectively. The earlier
reader editions added 9 and 12 tests. The final report package adds 8 tests.
See the [final validation record](../reports/CHECKS.md) for the current rerun.

## Read and rebuild the reports

The longer archived reader editions also have source-bound checks for their
tables and selected examples. These make no network requests:

```sh
python3 studies/summary-laundering/report/reader/evidence.py --check
python3 studies/wrong-goal-proof/reports/reader/check_report.py
```

The [final PDFs and LaTeX sources](../reports/README.md) are included, with their
own build commands. For the archived editions' exact example sources and checks,
read the [summary report guide](../studies/summary-laundering/report/README.md)
or the [certificate reader guide](../studies/wrong-goal-proof/reports/reader/README.md).

PDF compilation is optional and uses a separate TeX toolchain. The reports were
built with existing cached Tectonic resources; running the Python checks does
not require TeX. Do not use an acquisition command just to verify a report.

## What these checks can and cannot establish

They can check that the tables, visible responses, tool effects and finite
mathematical claims agree with the saved data. Hashes help detect changes to
files and configurations. They cannot prove provider origin, reproduce hidden
reasoning, remove dependence between similar tasks, or establish general model
safety. The [reports](../reports/README.md) keep those limits explicit.
