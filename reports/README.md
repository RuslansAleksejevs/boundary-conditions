# Final reports

These are the current, author-approved report versions, dated **9 November 2026**.
Each is a separate three-page paper: two pages of question, experiment, results
and conclusion, followed by limitations, ethics, references and AI-use disclosure.
Neither paper discusses the other.

| Report | Read | Source | Track |
| --- | --- | --- | --- |
| Prompt Injection at Agent Handoffs: The Second-Hand Instruction Problem | [PDF](prompt-injection-at-agent-handoffs-the-second-hand-instruction-problem.pdf) | [LaTeX](prompt-injection-at-agent-handoffs-the-second-hand-instruction-problem.tex) | 3; also fits 2 |
| A Certificate Is Not the Answer | [PDF](a-certificate-is-not-the-answer.pdf) | [LaTeX](a-certificate-is-not-the-answer.tex) | 4 |

Author: **Ruslans Aleksejevs**. Affiliation: **UC Berkeley**. The affiliation is
not a claim of university endorsement. Finalizing or publishing a report is not
the same as submitting it to the competition; no receipt or acceptance is claimed.

## What changed

The reports were shortened and renamed after author feedback. They now make
the question, experiment, numerical result and conclusion explicit, with two
tables and two selected examples each. The certificate study's track was
corrected from 2 to 4 to match its focus on oversight of a planted error.

The experiments, saved responses, scoring and conclusions did not change.
Earlier PDFs and their sources are preserved in the [report archive](../docs/ARCHIVE.md).
Examples were chosen after the run for explanation, not as evidence of frequency.

## Check the reports

From the repository root:

```sh
python3 reports/check_reports.py
python3 reports/check_reports.py --pdf
```

The first command uses only Python's standard library. It checks data counts,
uncertainty, exact examples, report elements and the published file hashes.
The optional second command also checks the three-page layout, titles, affiliation,
tracks and text boundaries; it needs Poppler's `pdfinfo` and `pdftotext`.
Neither command contacts a model or writes scientific data.

[Validation record](CHECKS.md) · [File hashes](manifest.json) ·
[Full reproduction guide](../docs/REPRODUCE.md)

## Build from LaTeX

With Tectonic 0.16.9 and its already-cached packages, run from this directory:

```sh
tectonic --only-cached --untrusted --keep-logs prompt-injection-at-agent-handoffs-the-second-hand-instruction-problem.tex
tectonic --only-cached --untrusted --keep-logs a-certificate-is-not-the-answer.tex
```

Both use [report-style.tex](report-style.tex). Building a PDF is optional: the
compiled files are included. PDF bytes may differ after rebuilding because of
toolchain or metadata differences. The manifest identifies this published
edition; update it only for an intentionally reviewed new edition.