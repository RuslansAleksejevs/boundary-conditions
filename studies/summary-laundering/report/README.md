# Reports: where to start

Read the final **[Prompt Injection at Agent Handoffs: The Second-Hand Instruction
Problem](../../../reports/prompt-injection-at-agent-handoffs-the-second-hand-instruction-problem.pdf)**.
It has three total pages, including its appendix and references. Its
[LaTeX, hashes and checks](../../../reports/README.md) are in the final report
package. The author approved it; submission and acceptance are not claimed.

The versions below are historical presentations of the same preserved evidence.

| Report | What it covers | Status |
| --- | --- | --- |
| [Reader edition](reader/who-said-that.pdf) · [source](reader/who-said-that.tex) | Completed main study, pilot history, failures, uncertainty, real examples and study-only accounting | Archived six-page edition, earlier title |
| [Earlier main report](main-report.pdf) · [source](main-report.tex) | Detailed main-study presentation at its original cutoff | Preserved nine-page historical draft |
| [Development report](paper.pdf) · [source](paper.tex) | Development pilot only; its “main not yet acquired” wording is historical | Preserved eight-page historical draft |

The older PDFs, TeX sources and experimental exports have not been revised to
match the reader edition. Their chronology matters: development and held-out
observations must not be pooled.

## Evidence and checks

- [Main public evidence](../results/main-2026-11-09/README.md): 60 input variants,
  40 paired clusters, 480 scheduled executor cells, all public responses and
  failures, and the frozen analysis.
- [Development evidence](../results/pilot-composite-2026-11-08/README.md): the
  separately disclosed interrupted and continued development pilot.
- [Reader build and source map](reader/README.md): exact example selection,
  source pointers, counts and offline build commands.
- [Reader validation record](reader/CHECKS.md): real checks, peer-review scope,
  PDF identity and preservation checks.
- [Historical report tools](TOOLS.md): original report build instructions and
  the unchanged public replay checker.
- [Harness commands](../RUNNING.md): detailed CLI, fixtures, freeze and replay.

From the repository root, the reader evidence can be checked without an API,
credentials, a model or third-party Python packages:

```sh
python3 studies/summary-laundering/report/reader/evidence.py --check
python3 -m unittest discover -s studies/summary-laundering/report/reader -p 'test_*.py' -v
```

The separate PDF check needs the local Poppler commands `pdfinfo` and
`pdftotext`; PDF rebuilding needs an existing cached Tectonic installation.
Neither step is needed to replay the scientific evidence.
