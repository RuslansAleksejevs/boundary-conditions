# Reader edition: release checks

Checked 9 November 2026. This record concerns a new presentation of existing
observations. **No model request, new experiment, response repair or regrading**
was performed to make the reader report.

## Report identity

- File: [who-said-that.pdf](who-said-that.pdf)
- Six total pages, including references and the mandatory appendix; 59,180 bytes.
- Abstract: 203 words. The first-page repository URL is clickable and precedes it.
- SHA-256: `d4cd2731157eb580944e5c8f7d827b8ad84900a4dcf78abaef26a1c98b5885da`.
- Title, author and subject metadata are set; no affiliation or human approval is
  asserted. Human author review and competition submission remain separate.

## Checks actually run

Commands below run from the repository root unless noted. Python was 3.14.6.
All Python checks were offline and made zero API requests.

| Command | Observed result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s studies/summary-laundering/tests -v` | 166 tests passed in 6.904 seconds |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s studies/summary-laundering/report/reader -p 'test_*.py' -v` | Nine additional reader tests passed in 0.178 seconds |
| `PYTHONDONTWRITEBYTECODE=1 python3 studies/summary-laundering/report/reader/evidence.py --check` | Main and pilot public replays passed; 18 source hashes, two source-bound examples, all derived artifacts and frozen scientific inventory checked |
| `PYTHONDONTWRITEBYTECODE=1 python3 studies/summary-laundering/report/check_public.py studies/summary-laundering/results/main-2026-11-09` | 60 inputs, 480 outcomes, 548 visible calls and both primary contrasts reproduced |
| `PYTHONDONTWRITEBYTECODE=1 python3 studies/summary-laundering/report/reader/check_pdf.py` | Six pages, 203-word abstract, clickable opening link, three exact quotations and disclosure/privacy checks passed |
| `tectonic --only-cached --untrusted who-said-that.tex` from this directory | Tectonic 0.16.9; cached resources only; no TeX warning or resource download |

The PDF was rasterized and **all six pages** were visually inspected at release:
the first-page URL and abstract, methods diagram and stage table, results and
uncertainty tables, both exact examples, conclusion/reproduction/references and
mandatory appendix. No clipped text, overlapping table cells or spill page was
found. Automated quotation matching normalizes Unicode and whitespace only; it
does not repair or rescore the actual fenced model response.

## Preservation and review

The release is based on main `7e2780c1357dcb0ce14b749caf222fd1080bad06`.
The historical pilot PDF is
`594743ca9e438864990bdf50c38c0e69b389ad3e9f387ff1df719413d9890da9`;
the historical main PDF is
`1e73de8ac9b0cd882d83ef13694e896d22913cd9a096350f43fb68919addcb45`.
An independent byte comparison to that baseline preserved **all 59 existing
non-Markdown files in this study**, including scientific modules, tests,
configuration, experimental JSON, old TeX and both historical PDFs. The scientific
body of `PLAN.md` is unchanged; only its historical-status banner changed.
`HISTORY.md` retains the complete earlier prefix. The release is confined to this
study's directory. A local-link check passed all 66 Markdown links in changed or
new documentation, and a private-path/credential/coordination-identifier scan
found no exposed values. Literal privacy-test patterns are not secret values.

Read-only internal cross-review read the full manuscript, reporting helper,
source pointers and PDF text; independently reran the main/pilot replay, nine
reader tests and PDF checks; and checked the examples, selectors, denominators,
uncertainty, accounting and cited abstract metadata. No blocking issue was
reported. That review did **not** claim a raster inspection, a full 166-test
rerun, private provider/account authentication or independent empirical
replication. The coordinator separately checked the evidence and a six-page
visual contact sheet. Three final editorial suggestions clarified the executor
columns, removed an implication of template independence and set PDF metadata.

These are internal AI-assisted code and report checks, not external scientific
peer review. The evidence still comes from one fixed hosted model and synthetic
tasks; missing responses and unresolved receipt costs remain unknown. Zero
observed harm is not evidence of equivalence or universal safety.
