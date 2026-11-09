# How the work unfolded

We started with two questions, built small test environments, and ran one fixed
evaluation for each. Neither evaluation produced the target failure. The record
below includes unsuccessful development attempts as well as completed runs.

**All times are UTC.** Times come from Git history, saved request timestamps and
dated audit records. Earlier lab-log headings sometimes use the California date;
for example, 7 November at 23:26 PST is 8 November at 07:26 UTC.

## From question to result

| Date and time (UTC) | What happened | What it established |
| --- | --- | --- |
| **8 Nov, 07:26** | Published the two designs, shared protocol and related-work notes. | A plan, not a result. The hypotheses did not assume that an attack would succeed. [First commit](https://github.com/RuslansAleksejevs/boundary-conditions/commit/b232b15). |
| **8 Nov, 08:16–08:54** | Integrated both offline test environments after code review. | Scorers, state changes and exact Boolean checks worked on software fixtures. No experimental model calls yet. [PR #1](https://github.com/RuslansAleksejevs/boundary-conditions/pull/1), [PR #2](https://github.com/RuslansAleksejevs/boundary-conditions/pull/2). |
| **8 Nov, 19:48** | Confirmed the $50 balance and fixed Qwen/Alibaba as the experimental route. | Limits were set before inference: $30 for summaries, $20 for certificates. [Budget and settings](docs/EXECUTION_BUDGET.md). |
| **8 Nov, 20:11–20:12** | The first handoff-study pilot stopped after one request. | Our transport parser rejected a repeated final usage message. The failed request was saved; a narrow parser correction followed. |
| **8 Nov, 20:17–20:23** | Its repaired pilot stopped after 59 attempts, including five technical retries. | API throttling left the planned pilot incomplete: 47/108 valid roles, below the fixed threshold. This failure was not erased. |
| **8 Nov, before 20:36** | Set slower request spacing and one active acquisition at a time. | A documented operational amendment, not a change to the model, attack prompts or scorer. [What changed and why](docs/OPERATIONAL_AMENDMENTS.md). |
| **8 Nov, 20:36–20:59** | Ran the certificate-study pilot: 20 original contracts. | It passed at 50/52 valid roles and 11/12 clean originals correct. One malformed translation and its blocked review were retained. |
| **8 Nov, 21:03** | Froze the certificate study's main cases, source and analysis. | The final set was fixed before its model responses were collected. [Freeze record](studies/wrong-goal-proof/results/live-main-2026-11-08/freeze.json). |
| **8 Nov, 21:08–21:26** | Finished only the 54 never-attempted summary-pilot roles. | The combined pilot passed at 99/108 valid roles and 29/32 clean checks correct. Earlier answers and failures were unchanged. [Combined pilot](studies/summary-laundering/results/pilot-composite-2026-11-08/README.md). |
| **8 Nov, 21:30** | Froze the summary study's main cases, source and analysis. | 40 attacked inputs plus 20 clean counterparts, each checked in eight conditions. [Freeze record](studies/summary-laundering/results/MAIN_FREEZE.md). |
| **8 Nov, 21:51–23:44** | Ran the certificate study's main evaluation: 100 original contracts, 260 scheduled roles. | No false guarantee observed. All 40 planted substitutions were correctly handled under all three labels; natural completion was 36/40. [Main results](studies/wrong-goal-proof/reports/main/README.md). |
| **8 Nov, 23:53** | Started the summary study's main evaluation after the certificate run ended. | The previously fixed schedule had 60 inputs and 540 roles. No simultaneous model acquisition. |
| **9 Nov, 00:11** | Integrated the certificate study's audited data and first full report. | [PR #4](https://github.com/RuslansAleksejevs/boundary-conditions/pull/4) merged after review while the summary evaluation continued. |
| **9 Nov, 03:04** | Completed the summary study's main evaluation. | No unauthorized state change in 478 returned executor responses; 443/480 scheduled checks completed the intended task. [Main results](studies/summary-laundering/results/main-2026-11-09/RESULTS.md). |
| **9 Nov, 03:09** | Reconciled the final account balance after both acquisitions ended. | Actual API usage was $3.75323494, leaving $46.24676506. Unknown individual charges kept their conservative bookkeeping reserves. |
| **9 Nov, 03:28** | Integrated the summary study's audited data and first full report. | [PR #3](https://github.com/RuslansAleksejevs/boundary-conditions/pull/3) merged after review. Both study releases were now in the main branch, without conflicts. |
| **9 Nov, after 03:28** | Repeated the integrated software tests and public-data checks. | 365 tests passed. Both data checks passed without new model calls. [Detailed completion record](RESEARCH_LOG.md#2026-11-09--both-held-out-studies-complete-audited-and-integrated). |
| **9 Nov, from 04:42** | Began a reader-first rewrite of the repository and two separate short reports. | Presentation work only: clearer explanations, result tables and examples tied to saved records. Old reports, scientific code and experimental data stay unchanged. |
| **9 Nov, 05:20** | Integrated the six-page *Verified, but What?* reader report and clearer study navigation. | [PR #5](https://github.com/RuslansAleksejevs/boundary-conditions/pull/5) merged after source and layout review. The other reader edition and shared documentation are still local at this checkpoint. |
| **9 Nov, after 06:14** | Rewrote both reports as independent, three-page LaTeX papers after feedback that the six-page editions were too dense. | Same experiments and conclusions; less operational detail, two result tables and two recorded examples per paper. |
| **9 Nov, by 06:42** | Confirmed the final titles and UC Berkeley affiliation. | *Prompt Injection at Agent Handoffs: The Second-Hand Instruction Problem* and *A Certificate Is Not the Answer*. These replace the earlier working titles. |
| **9 Nov, after 08:08** | Finalized both PDFs after author review, removed draft labels and checked the compiled pages. | Local final files were ready for the author's own submission; no receipt was claimed. Earlier PDFs were preserved. |
| **9 Nov, before 09:15** | Audited GitHub against the local final files and reassessed track fit. | Code and experimental results were public, but final PDFs and shared navigation were not. Recommended primary Track 3 (also 2) for handoffs, Track 4 for certificate oversight. |
| **9 Nov, from 09:15** | Author approved the track correction and a coherent public final release. | Corrected the certificate PDF to Track 4; assembled final PDFs/LaTeX, simplified navigation, the full timeline and an explicit archive. Validation and integration are recorded in the [release checks](reports/CHECKS.md). No new model experiment. |
| **9 Nov, 09:32** | Integrated the final report and documentation release. | [PR #6](https://github.com/RuslansAleksejevs/boundary-conditions/pull/6) merged without conflicts. Both final PDFs, LaTeX sources, checks, timeline and archive are public on `main`; 394 local tests passed. |

The main runs were sequential. Writing and review overlapped with acquisition,
but neither completed answer nor held-out case was replaced to obtain a preferred
result. The brief main-stage approval pause is preserved in the
[lab log](RESEARCH_LOG.md), together with the longer operational history.

## What actually ran

A **scheduled role** is one planned model response. An **HTTP attempt** is an
actual request, including permitted technical retries. A dependent role may not
be sent when the preceding response is invalid. Neither count is a count of
independent scientific tasks.

| Study and stage | Scheduled roles | HTTP attempts | Outcome |
| --- | ---: | ---: | --- |
| Summary: initial pilot | 108 planned | 1 | Stopped on an interface error. |
| Summary: repaired pilot and continuation | 108 | 113 | 99 valid roles; pilot gate passed. The 59 interrupted attempts and 54 new ones are counted once. |
| Summary: main evaluation | 540 | 548 | 60 valid summaries; 445 valid, 33 invalid and 2 missing executor responses. |
| Certificate: pilot | 52 | 51 | 50 valid roles; pilot gate passed. |
| Certificate: main evaluation | 260 | 259 | 253 valid roles, 4 invalid responses and 3 dependent reviews not sent. |
| **All physical attempts** | — | **972** | Includes development, errors and technical retries. |

The pilots tested whether the interface and ordinary tasks worked. They were not
pooled with the main results to increase the sample. A pilot could pass even if
no attack succeeded.

## How to read the evidence

- **Plans:** what we intended to test, written before the main observations.
- **Data:** the saved model responses and exact program checks.
- **Reports:** our explanation of those observations, with uncertainty and limits.
- **Software tests:** checks of the implementation, not additional model results.

The public files support offline replay, not a signed attestation from the model
provider. Final reports have author approval; competition submission and judging
are separate, and no receipt or acceptance is claimed. See the
[reading guide](docs/README.md) for the full map.
