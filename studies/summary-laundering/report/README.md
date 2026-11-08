# English research draft and reproducibility

`paper.tex` is a standalone **development-pilot-only draft**, pending author
review. The named author is Ruslans Aleksejevs; no affiliation or final approval
is asserted. It includes methods, actual results, uncertainty, utility, exact
failures, experimental cost, AI-use disclosure, references, and the mandatory
limitations/dual-use appendix. It is not a submission or a completed main study.

The empirical data are the separately exported amended development pilot in
`../results/pilot-composite-2026-11-08/`. The original failed pilot and interrupted
repair remain preserved. The prospective main corpus has not been acquired or
published. Do not change the frozen scientific modules to improve pilot effects.

From the repository root:

```sh
python3 -m unittest discover -s studies/summary-laundering/tests -q
python3 studies/summary-laundering/report/check_public.py studies/summary-laundering/results/pilot-composite-2026-11-08
```

Build the PDF from this report directory with an existing TeX installation:

```sh
tectonic --only-cached --untrusted paper.tex
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