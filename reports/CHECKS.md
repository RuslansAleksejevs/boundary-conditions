# Final edition: validation and integration

Edition: **9 November 2026**. These are local checks of saved observations,
not external peer review, GitHub CI or new model experiments.

## Report identity

| Report | Total pages | Abstract words | Primary track |
| --- | ---: | ---: | ---: |
| Prompt Injection at Agent Handoffs: The Second-Hand Instruction Problem | 3 | 159 | 3 |
| A Certificate Is Not the Answer | 3 | 170 | 4 |

Exact PDF and source hashes are in [manifest.json](manifest.json). Both reports
have the approved titles, Ruslans Aleksejevs / UC Berkeley, a repository link before
the abstract, two result tables, recorded examples, limitations, ethics and AI-use
disclosure. The handoff PDF is unchanged from the approved local final. The
certificate PDF was rebuilt to correct its track from 2 to 4; results are unchanged.

The private final-report checker passed after rebuilding: expected counts and
intervals, both example pairs, all 16 Boolean states, candidate certificate hashes,
three pages each, page boundaries, margins, affiliation and no draft markers.
The certificate rebuild used Tectonic 0.16.9 with cached resources and shell
execution disabled. An initial sandbox invocation failed in macOS system-network
initialization before compilation; the reviewed retry completed without TeX warnings.

## Reproducible checks

Run from the repository root. Every command below is offline.

```sh
python3 reports/check_reports.py --pdf
python3 -m unittest discover -s reports -p 'test_*.py' -q
python3 docs/check_links.py
python3 -m unittest discover -s studies/summary-laundering/tests -q
python3 -m unittest discover -s studies/summary-laundering/report/reader -p 'test_*.py' -q
PYTHONPATH=studies/wrong-goal-proof python3 -m unittest discover -s studies/wrong-goal-proof/tests -q
python3 -m unittest discover -s studies/wrong-goal-proof/reports -p 'test_*.py' -q
python3 -m unittest discover -s studies/wrong-goal-proof/reports/reader -p 'test_*.py' -q
python3 studies/summary-laundering/report/reader/evidence.py --check
python3 studies/wrong-goal-proof/reports/reader/check_report.py
```

## Results on the assembled release

Recorded on 9 November 2026 using Python 3.14.6:

| Suite | Tests | Result |
| --- | ---: | --- |
| Handoff study | 166 | PASS, 6.139 s |
| Handoff reader bindings | 9 | PASS, 0.199 s |
| Certificate study | 171 | PASS, 22.429 s |
| Certificate reporting | 28 | PASS, 0.344 s |
| Certificate reader bindings | 12 | PASS, 0.106 s |
| Final report bindings | 8 | PASS, 0.072 s |
| **Total** | **394** | **All passed** |

Both reader evidence checks passed. The handoff check bound 18 source files and
both selected examples; the certificate check preserved 91 earlier files and
replayed the saved campaign. An additional coordinator audit confirmed that all
142 non-Markdown study files present at `7e2780c` are unchanged, and historical
study logs retain their earlier contents.

The final report check passed with and without `--pdf`. Local Markdown file
targets passed the repository-wide check. Git whitespace checks passed. The
changed first page of the certificate PDF was visually inspected; the final
report checker checked text boundaries on all six pages. The handoff PDF was
not rebuilt or altered.

The original reader branch is preserved in the release ancestry, not presented
as the latest paper. No branch history was rewritten. Public integration is a
separate step recorded in the repository's PR history. **New model calls: 0.**
The last verified API spend remains $3.75323494, not the $50 authorized ceiling.