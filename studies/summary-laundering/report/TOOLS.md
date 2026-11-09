# Historical report builds and reporting tools

Start with the [report guide](README.md) for the new reader edition. This page
preserves the detailed build and audit notes for the earlier reports.

`main-report.tex` and `main-report.pdf` are the separate **completed held-out main
draft**, pending human author review. Main evidence is in
`../results/main-2026-11-09/`: 540 scheduled roles, 548 physical calls, 445 valid,
33 invalid and two missing executor cells. Useful correctness is 443/480 scheduled
cells. No observed executed forbidden effect or schema-valid protected write was
found; the primary contrasts remain uncertain, not evidence of equivalence or
universal refusal. Main and development observations are never pooled.

The original `paper.tex`, its included files, compiled `paper.pdf` and pilot
exports are preserved as the historical development checkpoint. Their statements
that main was not yet acquired describe that earlier cutoff, not current status.

`paper.tex` is a standalone **development-pilot-only draft**, pending author
review. The named author is Ruslans Aleksejevs; no affiliation or final approval
is asserted. It includes methods, actual results, uncertainty, utility, exact
failures, experimental cost, AI-use disclosure, references, and the mandatory
limitations/dual-use appendix. It is not a submission or a completed main study.

The empirical data are the separately exported amended development pilot in
`../results/pilot-composite-2026-11-08/`. The original failed pilot and interrupted
repair remain preserved. At that historical cutoff the main corpus had not been
acquired or published. Do not change frozen scientific modules to improve results.

From the repository root:

```sh
python3 -m unittest discover -s studies/summary-laundering/tests -q
python3 studies/summary-laundering/report/check_public.py studies/summary-laundering/results/pilot-composite-2026-11-08
python3 studies/summary-laundering/report/check_public.py studies/summary-laundering/results/main-2026-11-09
```

Build the PDF from this report directory with an existing TeX installation:

```sh
tectonic --only-cached --untrusted paper.tex
tectonic --only-cached --untrusted main-report.tex
```

The offline Python harness needs no third-party packages. PDF compilation is a
separate optional toolchain; `--only-cached` does not download a TeX bundle.
Local build logs and intermediate files are not research observations.

The local PDF build uses Tectonic 0.16.9 with cached resources only. The abstract
has 208 words. Focused read-only peer review found no blocking report or public
subset issue and independently reproduced the public-data check. That review
did not rerun the full test suite or authenticate private SSE/provider billing.
The report is eight pages: six main pages including references and a two-page
mandatory appendix. The reviewed build has no TeX warnings; title, result table,
uncertainty figure and reproduction command were visually checked.

`export_results.py` generates immutable public bundles from separately audited
private runs. Its `--main` option is only for an actually acquired, audited main
bound to the passing composite pilot. `check_public.py` reconstructs visible
JSON parsing, mock state transitions, summary/request identities, condition
tables and primary statistics. It cannot authenticate provider history, private
approvals, the complete SSE stream or wallet. No helper sends model requests.

The SVG and all JSON tables derive from the frozen analysis. The paper's pilot
figure displays the same two zero estimates and full-range conservative
intervals. Degenerate bootstrap intervals are never presented as proof of
equivalence. The lexical case readings are illustrative, not semantic labels.

The separate main build uses the same cached Tectonic 0.16.9 toolchain. It has
nine pages (six main text, one references, two appendix), a 204-word abstract
and no TeX warnings after correcting two line overflows. The main condition
table, paired-uncertainty figure and reproduction page were visually inspected.
The account-agreement note is a dated accounting observation, not a change to
unknown receipts, reserves or frozen scientific calculations.