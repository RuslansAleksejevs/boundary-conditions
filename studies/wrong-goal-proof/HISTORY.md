# Study history

Append-only engineering and research record. Plans and test doubles are not model
observations. Dates are UTC unless explicitly stated otherwise.

## 2026-11-08 — Initial implementation and ground-truth validation

PROJECT_REPORTED; sources: code in `wgp/`, tests in `tests/`, and local commands.
Implemented strict Boolean AST and controlled rendering, scalar exhaustive solver,
independent bit-vector verifier, separate open-function and closed-claim checks,
all four injected-fault and all four equivalent-rewrite families, a 20-case
development set and 100-case engineering holdout, semantic/skeleton split checks,
natural/replay pipelines, offline adapters, manifests, freeze rehearsal, and analysis.

The first 56-test run found one failure: Python 3.14 accepted JSON nesting deeper
than the test expected. Added an explicit nesting bound instead of relying on
interpreter recursion behavior. The subsequent expanded 97-test suite passed in
5.378 seconds. It includes 2,400 random ASTs, all 256 three-atom Boolean functions,
600 randomized solver/checker contracts, and malformed certificate checks.

Read-only peer review confirmed the scope distinctions and proposed stronger
response/status consistency checks. Implemented those checks, incremental event
logging, full-schedule paired missingness bounds, and additional regression tests.
The final pass and measured rehearsal outputs will be recorded separately.

No real model experiment or external experimental spending occurred. Local
test-double behavior is explicitly synthetic. No competition submission occurred.

## 2026-11-08 — Expanded integrity suite passes

PROJECT_REPORTED; command:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=studies/wrong-goal-proof python3 -m unittest discover -s studies/wrong-goal-proof/tests -q`.
104 tests passed in 4.556 seconds on Python 3.14.6. Added standalone false-guarantee
packet export/verification and tests for certificate, witness, hash, claim and
duplicate-case corruption. Request/response/status consistency, Boolean score
types, invocation flags, latency, and incremental journals are now checked.
Documented engineering-versus-empirical holdout, offline chronology limitations,
the 12-original-clean-case pilot denominator, and missingness bounds.
No real pilot or confirmatory LLM holdout has run or been frozen.

## 2026-11-08 — Pre-publication implementation check

The same unittest command passed 105 tests in 5.611 seconds on Python 3.14.6.
The additional regression verifies that invalid Unicode is recorded as a schema
error rather than an unhandled exception. Normalized final newlines, reviewed
the staged study-only paths, and scanned for personal paths, credentials and
private coordination identifiers; no matches were found. No experimental model
calls or spending occurred. The implementation is ready for synthetic rehearsals.

## 2026-11-08 — Six audited synthetic rehearsals

Implementation commit `c15e8401a9c41f4bf73deee3a02bdbf82394cc47`; Python 3.14.6;
seed 6006. Saved perfect and local-only development/freeze/engineering-holdout
chains, plus abstaining and malformed development runs. Total: 728 local adapter
invocations and 616 reviewer outcomes across six runs, zero experimental model
calls, zero new external experimental cost. The two failed pilots were retained;
CLI freeze returned exit 2 and did not create their freeze files.

On the 40 planted engineering originals, perfect/local-only doubles produced
0/40 and 40/40 false SAFE in each of B/N/S, respectively. Both had natural utility
40/40 and equivalent-control utility 20/20 in each arm. Both scope contrasts are
zero by the scripted behavior, not empirical null results. Standalone evidence
verification confirmed all 40 originals and 120 scripted false guarantees.

Prepared reviewed aggregate JSON and a complete synthetic counterexample packet;
run/profile hashes are recorded in results/RECORD.json. All actual counts, commands,
uncertainty caveats, and limits are in VALIDATION.md. The engineering holdout is
explicitly not an untouched or preregistered confirmatory LLM evaluation.

All six saved runs were re-audited before publication. Recomputed analysis matched
each public aggregate exactly; the exported packet matched the audited local run,
and every file hash in results/RECORD.json matched. Repository diff checks passed.

## 2026-11-08 — Study branch published for coordinator review

Pushed the study-only implementation and reviewed synthetic results to
`study/wrong-goal-proof`, then opened
https://github.com/RuslansAleksejevs/boundary-conditions/pull/2 into `main`.
Implementation commit: `c15e8401a9c41f4bf73deee3a02bdbf82394cc47`;
rehearsal/results commit: `b851d515fbcd43f5ab1065412c7c3f2ff6ce85bf`.
Fetched the current upstream and confirmed the PR diff changes only this study.
Staged privacy/path scans found no personal paths, credentials, or private
coordination identifiers. No direct main push, force-push, or self-merge occurred.

Read-only reciprocal review is complete; the integration coordinator will perform
the merge decision. Opening this PR is not integration or contest submission.
The deterministic validation remains 105 passing tests and six audited synthetic
runs, with zero experimental model calls. Future empirical work remains blocked
on an approved interface, configuration, budget and fresh prospective holdout.

## 2026-11-08 — Authorized live-stage preparation

After explicit start authorization, fetched upstream and created
`study/wrong-goal-proof-live-v1` from main `afd055c`, preserving the prior branch.
The baseline 105 tests passed in 4.375 seconds. Allocation for this study is USD20,
not the combined project budget. Core schedule remains 52 pilot +260 evaluation;
up to 15 identical technical retries and one genuine-interface-correction pilot
are reserved within the same allocation. No extra model or experimental arm.

Credential availability and the common coordinator preflight remain blockers to
acquisition. Preparation adds cross-bundle exclusions and a separately audited
live transport/ledger while preserving offline-only guards. No secret attachment,
credential bypass, or inference attempt occurred during this preparation.

## 2026-11-08 — Live preparation and 146-test validation

Implemented the separate official-HTTP acquisition path, strict live/campaign
audit, immutable preparation/freeze commands, cross-bundle exclusions and actual
translator-output/main separation check. The persistent hash-chained wallet
reserves before HTTP, fsyncs, retains unknown/abandoned charges, and enforces the
USD20 /379-attempt /15-extra-technical-attempt limits across stages and restarts.
Requested completion cap and the approved financial output margin are separate.
Provider identity, data policy, no fallback/redirect, receipt/request binding,
duplicate acquisition IDs and actual pilot/ledger binding are checked explicitly.

The original offline auditor was not widened to admit live metadata. Transport
fixtures cannot qualify a real pilot, revision or freeze. Mathematical evidence
verification remains separate from provider-origin claims. The union of actual
candidate functions from all preserved pilots is checked against main. Collision
blocks freeze and cannot justify a repeated pilot; no post-outcome automatic
resampling exists. Solver/scalar/vector/certificate algorithms did not change.
No extra experimental model or arm was introduced.

Exact final command:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=studies/wrong-goal-proof python3 -m unittest discover -s studies/wrong-goal-proof/tests -q`.
Result: **146 tests passed in 20.539 seconds**, Python 3.14.6 (105 original tests
+41 new tests). `git diff --check` and `run_live.py --help` also passed.
An earlier 128-test run found a Decimal reservation bug; it was corrected.
The expanded 144-test run initially exposed two test-harness assertions, which
were corrected; the complete 144-test rerun passed before the leakage tests.
Read-only peer review independently identified the Decimal issue and the omitted
first-pilot exclusion in the repeat path. Both fixes were independently reread;
the reviewer did not run this suite or assert live API access.

All new calls were explicitly labeled, in-process transport fixtures in unit
tests. **Actual experimental model requests: 0; new external experimental cost:
USD0.** Assistant-session costs are not measured or claimed to be zero. No secret
attachment/read/bypass was attempted. Approved credential availability and final
tariff/settings/source-bound coordinator GO remain unresolved. No real pilot,
main evaluation, findings, or empirical PDF is claimed. These are external
blockers, not a reason to invent another synthetic experiment. Public LIVE.md
documents the intended authorized commands. Upstream was fetched before preparing
publication; only this study's paths are being changed.

## 2026-11-08 — Live preparation published as a draft, acquisition blocked

Committed the reviewed implementation as
`040b36dbd203e34c9f80180c266ea413e028b90c`, pushed
`study/wrong-goal-proof-live-v1`, and opened draft
https://github.com/RuslansAleksejevs/boundary-conditions/pull/4 into main.
Only 17 owned study files changed. Staged path/content checks found no private
paths, coordination identifiers or credentials. Ignored local bytecode is not
part of the publication. No force-push, direct main push or self-merge occurred.

Read-only peer review of the final source closed the union-of-all-pilots guard
and first-pilot collision/repeat-path issue. Final executable validation remains
146 passing tests in 20.539 seconds; this handoff changes documentation only.
The repository-wide private tracker check also passed. Shared competition state
and index updates remain the integration coordinator's responsibility.

The draft is not an integrated result, and it does not claim a live experiment.
Actual experimental requests and new external experimental cost remain zero.
Approved credential availability and final source/configuration/manifest-bound
coordinator preflight still block acquisition. No workaround or new batch was
attempted while waiting for these external requirements.

## 2026-11-08 — Renewed authorized execution and selected Qwen route

After a new explicit user start, continued the same branch and existing PR.
Approved credential availability was restored through the standard secret
mechanism; no credential value was read into messages, copied or printed.
The selected experimental target is Qwen3.5-122B-A10B via OpenRouter/Alibaba,
not the earlier unexecuted gpt-oss proposal. Official endpoint metadata was
rechecked: context 262,144, maximum prompt 258,048, maximum completion 65,536,
USD0.26 input/USD2.08 output per million, quantization unknown. Enabled reasoning
is supported; reasoning_effort is not advertised. The official contest page
again confirmed 8 November 23:59 AoE (9 November 03:59 PST).

Compatibility changes are being prepared before the exact code/configuration GO.
Full-context reservation for all 379 possible attempts is USD38.74750464, above
the unchanged USD20 study allocation. No guessed tokenizer bound or relaxed
wallet is used; the prospective campaign admission policy is under explicit
coordinator review. No inference has occurred during this preparation.

## 2026-11-08 — Qwen SSE and conservative billing preflight

Before any inference, the coordinator approved full 262,144-token reservations
for both input and billed output (USD0.61341696 per attempt). The earlier 16,384-
output proposal was withdrawn after native answer-versus-thinking token semantics
were checked. Streamed SSE is explicit, with an 8 MB wire cap, a 180-second hard
wall timer, one consistent assistant/model/provider identity, terminal finish,
final usage at or after finish, and DONE. Native reasoning_content as well as
reasoning/reasoning_details are removed before persistent records.

The explicit prospective budget amendment removes only the requirement to fund
all 379 worst-case attempts upfront. The per-dispatch full-context reservation,
hard USD20 persistent wallet, fixed schedule, technical retry and conditional
pilot limits remain. Mean/observed-maximum/full-context projections are available
from the pilot before main; budget-stopped cases remain unassessed.

Confirmed ledger charges now use max(provider-reported cost, no-cache token-price
bound), separately from reported API cost. Only complete valid billing releases
unused reserve; malformed/partial/missing-cost responses remain fully reserved.
Coordinator review caught interim usage being accepted before terminal finish;
that ordering defect was fixed and regression-tested. Reciprocal peer review
also checked route/cap/identity-before-settlement and joint total-context bounds.

Command unchanged:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=studies/wrong-goal-proof python3 -m unittest discover -s studies/wrong-goal-proof/tests -q`.
**159 tests passed in 23.014 seconds**, Python 3.14.6. The immediately preceding
158-test run passed in 21.500 seconds before the final usage-order regression.
No experimental model requests, paid experiment outcomes or empirical freeze
exist yet. An exact reviewed source/configuration/manifest GO is still required.

## 2026-11-08 — Pre-inference terminal SSE compatibility correction

The companion study's first real request exposed the provider's repeated empty
terminal choice in its final usage footer. This study still had zero model
requests. Added the exact sanitized terminal events as an attributed interface
fixture, not a wrong-goal-proof outcome. Acceptance is restricted to the last
event with final usage, identical finish/native-finish/identity, and empty allowed
delta fields. Hidden reasoning is still discarded before storage; its presence
is marked only as a Boolean so a hidden footer continuation also fails audit.
Tests reject nonfinal/no-usage/third terminals, changed finish, new content or
refusal, extra delta fields and hidden continuation. JSON test fixtures are now
included in the source inventory.

An initial 163-test run was invalidated when the fixture-inventory line was added
while that run was in progress: the existing source-change guard correctly
stopped its offline CLI audit/analysis (two failed assertions and one downstream
missing-file error). A full unchanged-source rerun is required. No scientific
logic, prompts, cases, scoring rule or sample size changed. The earlier unused
campaign preparation is retained; the replacement will use the same prospective
seed and dataset, not a repeat pilot or outcome-conditioned resampling.

The unchanged-source rerun completed successfully: **163 tests passed in 35.580
seconds**, Python 3.14.6, using the same full-suite command. No external inference
or experimental spending occurred during this compatibility correction.

## 2026-11-08 — Prospective transport pacing before the first study request

The companion study's rate-limited pilot stopped under its existing circuit.
Before this study's first model call, the coordinator's read-only account check
showed funding remained; the exact 429 source was unknown. Approved a prospective
20s minimum between HTTP attempt starts and a 60s minimum cooldown after 429,
respecting longer valid Retry-After up to 300s. Values above 300s stop instead of
being shortened; absent/invalid values use 60s. Runtime waits use a monotonic clock
and chunks no longer than 30s. This is not an extra pilot, model probe, budget
increase, resampling, or change to model parameters, prompts, gates or sample.

Added explicit manifest pacing metadata, virtual-clock tests, safe normalized
Retry-After seconds and allowlisted error-code/source/reason diagnostics. Raw
provider error bodies and arbitrary headers are not retained. The audit checks
recorded start spacing and post-429 cooldown. Shared-route use is serialized by
the coordinator. Existing source preparations are retained unused; the replacement
must preserve the exact dataset and obtain a new source-bound GO.

The complete unchanged-source suite passed: **171 tests in 28.092 seconds**,
Python 3.14.6, same command. Seven virtual-clock/no-network HTTP tests and one
SSE error-privacy regression supplement the prior 163 tests. The model call count
is still zero at this prospective amendment; pilot-v1 remains unused.

## 2026-11-08 — Original live pilot started under exact GO

The coordinator independently repeated 171 tests (39.727s), verified exact
configuration/source/manifest, 14 engineering exclusions and the unchanged fresh
dataset, and issued pilot-v1-only GO at 20:35:36Z. Acquisition source commit is
`83aa8ee313d4f054ac47af038a8b5c33a6a1e859`; existing draft PR #4 was updated.
The first planned natural translation began at 20:36:59Z through the official
OpenRouter API and approved ordinary secret attachment. No extra smoke call,
model change, unpublished resampling or shared-route concurrent study was used.

At 20:43:42Z, 14 actual HTTP200 replies had complete SSE and valid response
schemas, with known API cost USD0.12559222 across all 14 receipts. No retry or
HTTP429 occurred by that checkpoint. The first two natural C/Q translations
preserved the original open functions and final answers were correct. These are
interim operational observations; all 52 planned pilot roles remain in scope,
and no gate, freeze, main evaluation or confirmatory conclusion is asserted.

While acquisition continued with unchanged source inventory, added a separate
presentation-only figure renderer. Its four tests passed in0.004s using explicitly
fabricated count fixtures and no network. It does not rescore outcomes or acquire
responses. No empirical figure or report PDF has been generated yet.

## 2026-11-08 — Pilot completed and prospective main freeze prepared

The original live pilot finished20:59:48.911404Z after1369.875s. Full campaign
audit, pilot gate and standalone empty false-guarantee evidence verification all
passed. Fifty of52 scheduled roles were schema-completed; one translator emitted
malformed JSON and its dependent review was blocked. This was preserved, not
repaired or resampled. Eleven of12 clean originals were correct in all arms.
There were51 physical HTTP200 requests, no technical retries or HTTP429, no
unknown charges or pricing overruns. Actual API cost and conservative settled
wallet both equalUSD0.39923650. Input42437/output186636/reasoning184388 tokens
were reported across all51 receipts.

Natural utility was7/8, with0/7 drift among valid translations and one unassessed.
Planted false SAFE was0/8 in each B/N/S arm, with8/8 correct witnesses each;
equivalent utility was4/4 in each arm. The paired zero result is pilot evidence
only: bootstrap95=[0,0] is degenerate, while bounded-iid95 is approximately
[-0.960323,0.960323]. There were no actual false guarantees to place in the
evidence packet. Actual candidate/holdout separation passed with19 distinct
observed functions and0 overlaps; fourteen prior engineering bundles remained
excluded. No scientific prompt, task, scorer, sample or model was changed.

After receiving the complete checkpoint, the coordinator explicitly authorized
freeze preparation only. At21:03:14.925378Z, saved a prospective freeze for the
unchanged100 held-out originals/260 logical roles. Freeze digest is
`e5b6cc5c66c3698284e5af2145add1983a02b195067c23ef920c7a1c766dab7a`, binding pilot
`f696c9be737a22278b76b7f1bfa91527b1e8a23226ea5914e93e70b4111fb2c1` and source
inventory `87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e`.
No main API call or main GO exists at this snapshot. Shared-route handoff and
separate main authorization remain the next external step.

Pilot SVG/PDF was generated from actual audited analysis, rasterized and visually
checked with an explicit development/not-confirmatory label. A separate cached-
package Tectonic0.16.9 format check compiled successfully after reviewed host
access resolved a sandbox system-configuration failure; it is not an empirical
paper. Official template structure, bibliography metadata and mandatory ethics
appendix were prepared outside the frozen source inventory. Standalone report
result text and empirical PDF remain pending the actual main outcome or blocker.

## 2026-11-08 — Pilot-only report preview and publication boundary checks

At21:24Z, main acquisition and main GO remained pending the serialized shared
route. The acquisition inventory was unchanged. Nine presentation/export tests
passed in0.003s with fabricated-count/no-network inputs, separate from the171
acquisition tests. The coordinator reviewed the report/export/figure preparation
without a blocking finding; actual completed-main export and manual content
review remain required before publication.

Compiled a private six-page actual-pilot-only preview with cached Tectonic0.16.9.
The abstract contains240 words. Mandatory ethics and AI-use statements and the
human author name were checked; extracted text contains no private host path.
No overfull warning remained. Enlarged the chart text and visually checked its
in-page rendering together with exact pilot counts. No held-out results were
invented, no held-out corpus was published, and no competition submission was
performed. The preview and its private path wrapper are not public deliverables.

The unchanged-source rerun then passed171 acquisition tests in21.834s and9
presentation/export tests in0.004s. The first command mistakenly omitted the
documented PYTHONPATH and stopped at nine import errors before any tests ran;
the correct full command was:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=studies/wrong-goal-proof python3 -m unittest discover -s studies/wrong-goal-proof/tests -q
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s studies/wrong-goal-proof/reports -p 'test_*.py' -q
```

Campaign audit again passed with51 physical calls, zero false guarantees and
USD0.39923650. Source inventory remained
`87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e`.
No new API calls were made during these CPU checks.

## 2026-11-08 — Main-only GO passed; execution blocked before launch

After the companion explicitly released its route, the coordinator issued the
exact main-only GO at21:29:15Z. The unchanged-source main preflight passed with
zero calls. The paid260-role acquisition was submitted once to the execution
permission layer, which denied it before launch because it required new direct
user authorization rather than delegated GO alone. No retry, alternative
transport or smaller-call workaround was attempted. The shared route was
released while this external blocker is resolved.

Read-only verification at21:31:08Z found no main directory and exactly102 wallet
events, unchanged from the completed pilot. Full campaign audit still passed:
51 actual HTTP calls, zero confirmed false guarantees, zero technical retries
and known/settledUSD0.39923650. The100-original/260-role sample, source and freeze
were not changed. No model outcome was discarded and no holdout corpus released.
The next paid attempt requires new explicit user authorization accepted by the
execution layer and renewed exclusive-route coordination; no submission occurred.

## 2026-11-08 — Pilot-only report and bounded public evidence view

Prepared an English development-only PDF/Markdown snapshot with a 21:50 UTC
cutoff. It preserves the actual null planted result, malformed translation and
dependent blocked review. No held-out result is asserted. Public records contain
20 development originals, 52 logical roles, 44 reviewer outcomes and 51 visible
HTTP receipts. The full 100-case holdout and engineering-exclusion corpus remain
private. Original run, manifest, freeze and 102-event ledger copies were checked
byte-for-byte equal; the source run digest remains f696c9be737a22278b76b7f1bfa91527b1e8a23226ea5914e93e70b4111fb2c1.

The public-view verifier repeats unchanged mathematics, aggregate analysis and
physical-receipt usage and passes with zero actual false guarantees. It explicitly
does not reproduce the full acquisition or cross-split audit without the withheld
corpus. Its first integration check caught a reporting-code mismatch between
52 scheduled roles and 51 physical attempts; the verifier was corrected and the
existing immutable records then passed. No response, cost or source analysis was
changed. Eighteen reporting/publication tests passed in 0.284 s, including five
saved-pilot mutation checks. These are additional to 171 acquisition tests and
make no new model calls.

Read-only peer review reran the public verifier and found no scientific blocker.
Clarified the natural table to show 0/7 assessed false-SAFE answers, 7/8 correct
scheduled originals and one unassessed review. The exact purpose-written
scientific pilot authorization paragraph was independently compared to its private
original and approved for publication. This does not include private messages,
execution-review text, later authorization records or account responses. All 51
visible answer texts were manually inspected; privacy scans found no personal
host paths, credentials or hidden reasoning.

The portable report compiled with cached Tectonic 0.16.9 to six pages (five through
references, one appendix), with no TeX warnings after layout checks. Title,
table/figure and appendix were visually inspected. The abstract has 204
whitespace-delimited words in its TeX source. The earlier 240-word preview note
could not be reproduced and is corrected here; it does not change any empirical
number. Required ethics/limitations and AI-use statements are present, no private
path appears in extracted PDF text, and human author review remains pending.
The frozen acquisition inventory remains87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e.
No competition submission was performed.

## 2026-11-08 — Exact main acquisition started after renewed authorization

New stage-specific user authorization was verified in the execution-owning
context, which submitted the exact previously denied command once to a fresh
execution review. It passed and started the main process at21:51:10.093347Z.
This study worker did not launch a duplicate process, use another provider
interface or alter any frozen source, configuration, prompt, task, score or
sample. The100-original/260-role schedule, hardUSD20 study wallet and original
retry/circuit rules remain unchanged. The companion route remains idle.

The existing journal's early checkpoint at21:52:35.436624Z has three HTTP200
receipts and three schema-completed roles, with known main costUSD0.02207062.
The recorded model is qwen/qwen3.5-122b-a10b, providerAlibaba, complete SSE and
observed minimum start spacing22.670035s. One request was still in flight.
These interim operational counts are not a completed main analysis. The
pilot-only report is explicitly preserved as of21:50UTC, before main began;
no held-out task content is released while acquisition is ongoing.

## 2026-11-08 — Pilot report published while the fixed main continues

Fetched origin, reviewed all staged paths and privacy markers, checked append-only
history, and committed only 32 owned study files as
`8b431b26a6020bad9c98defd7a027ada5f34d6c5` (Report the real development pilot with
scoped replayable evidence). Pushed the existing study branch and updated draft
PR#4 in English. No force-push, direct main change, self-merge or submission was
performed. The last reporting-test rerun passed 18 tests in0.292s. The final PDF
has six pages, an explicit21:50UTC pilot cutoff, no TeX warnings, required ethics
and AI disclosures, and no private host paths in extracted text. The PDF was
also presented to the user; author review remains pending.

Read-only main checkpoint at21:58:31Z:17 HTTP200 receipts,17 schema-completed
roles and17 known costs totaling USD0.12502880; the last receipt finished at
21:58:03.924727Z. No completed run.json existed. The already-running acquisition
remains owned by its execution context; this worker starts no second process.
Frozen source and all scientific settings are unchanged. Full main audit,
analysis, counterexample verification and eventual public export remain pending.

## 2026-11-08 — First main formatting failure preserved without retry

By22:10:57Z the existing main journal contained47 HTTP200 receipts, with47 known
costs totaling USD0.37256648 for main. One translator returned malformed JSON:
438 visible characters, expecting a comma at character438. The dependent review
was correctly blocked. Logical statuses were46 completed, one schema error and
one blocked review, accounting for48 processed scheduled roles. No transport
failure, schema repair, semantic retry or sample replacement occurred. The run
continued; this formatting failure is unassessed, not demonstrated semantic drift.

Read-only review also prompted two documentation-only cutoff clarifications,
pushed as38329134118a0889c1696e3bc0551b7865147aa0. The source inventory and
published immutable pilot records/PDF remained unchanged. Current main results
will only be finalized after the whole run and full audit; public release of its
exact scientific authorization metadata requires its own scope review.

## 2026-11-08 — One hundred main receipts; fixed acquisition continues

At22:33:55.251661Z, the existing main journal held100 HTTP200 receipts and100
known costs totaling USD0.77680018. Including the completed pilot, known study
cost was USD1.17603668. There were101 processed scheduled roles:98 schema-valid,
two schema errors and one dependent blocked review. The second malformed answer
was a45-character reviewer response rejected at JSON character0; it was retained
without repair or semantic retry. No transport failure or completed run file
was observed. No interim semantic effect or final utility result is claimed.

The exact original scientific main authorization paragraph was separately read
and approved for publication only after acquisition completion, full audits and
content review. Its object must match the preserved original. This approval
does not cover private user-confirmation records, review text, account responses
or coordination messages. The21:29 scientific GO, later renewed execution
permission and21:51 start remain distinct chronological events. Frozen source
and all original task/analysis choices are unchanged.

## 2026-11-08 — Oracle reporting precision; main continues unchanged

Clarified manuscript wording about the original-AST oracle. Every B/N/S reviewer
already sees the full original task in unambiguous controlled notation. The code
control has direct access to a trusted structured reference AST and exhaustive
computation, not additional hidden task semantics. It is an engineering ceiling,
not an interface-/resource-matched empirical defense or a safety discovery.
This accuracy clarification changes no prompt, task, scoring rule, analysis or
acquisition source, and introduces no no-certificate/single-agent comparison.
The report source will be rebuilt and checked with the eventual main report.

Read-only checkpoint at22:46:45.871100Z:125 HTTP200 receipts and125 known main
costs totaling USD1.01474282. Processed126 scheduled roles comprise123 completed,
two schema failures and one dependent blocked review. No new error, transport
failure or completed run file was observed. Acquisition remains single-process
and unchanged; no interim scientific conclusion or additional API run is claimed.

## 2026-11-08 — Preserved schema failures and bounded automatic retries

The read-only23:12:04Z checkpoint has183 physical main receipts:181 HTTP200 and
two HTTP429. Known main cost is USD1.42809550; the two failed-attempt costs
remain UNKNOWN and both conservative full-context wallet holds are retained.
Processed184 roles comprise177 schema-completed, four schema errors and three
dependent blocked reviews. Two further malformed translator JSON responses
(358 and401 visible characters) were kept unassessed with dependent reviews
blocked. No schema repair, semantic retry, sample replacement or tuning occurred.

The429 receipts finished at22:55:37.420634Z and22:57:26.122099Z. Each was
followed by a successful existing same-role automatic retry, beginning
60.004940s and60.004454s after the failed response respectively. Only code429
was returned; no Retry-After or diagnosed cause is claimed. Exact payload
identity and full-run pacing remain final-audit checks. No extra API process
was launched. The original single main acquisition continues, without a
completed run file or interim scientific comparison.

## 2026-11-08 — Reproducible operational summary; 200 processed roles

Added presentation-only `reports/acquisition_summary.py` and ten no-network
tests, outside the prospectively frozen source inventory. Its public command
requires an ended main, complete native campaign audit and matching source.
The summary distinguishes decimal provider-reported costs from conservative
settlements, unknown full holds and unsettled reservations, and records physical
attempts versus scheduled/blocked roles. Same-role retry records include exact
payload identity and observed UTC cooldown; monotonic HTTP and stage durations
are labeled separately. It makes no inference about an HTTP429's cause and does
not replace the immutable wallet, mathematical scoring or private account review.
Eight fictional arithmetic/timing tests and two saved-pilot metadata replays bring
the reporting suite to28 passing tests in0.287s. No new task or API call occurred.
The full summary has not been run on the still-active main campaign.

At23:17:32.212810Z, the existing journal has199 receipts (197 HTTP200, two429),
with197 known main costs totaling USD1.51224684 and two unknown charges. Processed
200 of260 logical roles comprise193 completed, four schema failures and three
blocked dependent reviews. No new failure, halt or completed run file is present.
The frozen acquisition source inventory remains87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e.

## 2026-11-08 — Independent accounting review; 240 processed roles

Read-only review independently passed28 reporting tests in0.293s and found no
blocking functional issue. Clarified that each parsed provider cost is converted
via Decimal(str(value)); the summary does not preserve the original JSON wire
lexical spelling of a floating number. Manuscript wording now separates logical
roles from physical requests and states that sampling/independence assumptions
are not established merely by sharing generated templates. These are reporting
clarifications only, with no new scoring rule, source inventory or model call.

Latest receipt at23:35:55.308515Z:239 physical attempts,237 HTTP200 and two429;
known main cost USD1.84807792 with two unknown full holds. Processed240 of260
roles comprise233 completed, four schema failures and three blocked dependent
reviews. No additional error, halt or completed run file was present. Final
audit, summary, evidence and export still require completed main acquisition.

## 2026-11-08 — Frozen main completed; audited null and complete public package

The sole main process exited code 0 after completion at23:44:59.374908Z. All100
originals/260 roles remain in the fixed schedule. There were259 physical attempts
(257 HTTP200, two429),253 schema-valid roles, four schema errors and three blocked
dependent reviews. No sample replacement, schema repair, model change or additional
empirical probe occurred. No further study API acquisition is authorized.

Natural C/Q and closed-truth drift is0/37 valid translations, useful completion
36/40 and observed false SAFE0/36 assessed reviews. Five valid translations
changed syntax without changing either function. All four unassessed natural
originals were SAFE; their three malformed translations and one Markdown-fenced
review remain verbatim. The frozen generic missingness bounds [0,0.10] are not
post-hoc tightened. All20 natural UNSAFE witnesses pass. B/N/S each have0/40 false
SAFE and40/40 correct planted witnesses, and20/20 correct equivalent controls.
No abstention or false guarantee was observed; the independent false-guarantee
packet is empty. Primary S-B and secondary N-B are0 on40/40 complete pairs,
bootstrap[0,0], bounded-iid95%[-0.4294694083,0.4294694083]. Shared templates and
unestablished independence limit inference; this is not presentation equivalence
or general safety. Clean utility is56/60.

Full native campaign audit passed on private source and exact public export:
310 physical attempts and264 scheduled reviewer outcomes across both stages.
Private journal bindings passed for calls, outcomes, receipts and terminal hashes
(pilot200 events; main1000). Main digest is
`81af66525adfb197fb3c48911fb07c05c3668fa8f7c75987a6143aac54a636de`.
The exact approved scientific GO object matched, with preserved file SHA256
`55b13ad6cc7822751333c62ad101792acc5865cc0891c57d3bf63452de76f523`.
The earlier scientific GO and later renewed execution permission remain distinct;
private permission/review records are excluded from publication.

Main known cost USD1.99717180 plus pilotUSD0.39923650 gives known campaign
USD2.39640830 for308/310 attempts. Two unknown429 costs retain full holds
USD1.22683392; cumulative conservative commitment isUSD3.62324222, not an exact
bill. No unsettled reservation or pricing overrun. Same-role exact-payload retry
checks pass after60.004940s/60.004454s; observed UTC minimum start gap20.000076s.
Monotonic main elapsed time6829.286533s, mean/max HTTP23.964844/67.663923s.
Known main input/output/reasoning tokens210478/933869/921437 exclude two unknown
attempts. Output usage10723 and8283 exceeded requested8192 on two responses but
not the full-context bound; both finished with stop. No429 cause is inferred.

Unchanged acquisition suite:171 tests PASS21.591s. Reporting suite:28 tests
PASS0.289s; independent coordinator reruns passed171 in21.312s and28 in0.281s.
The14-file export inventory, privacy patterns, exact private/public run and
operational-summary equality passed. All37 valid translator answers,39 unique
valid reviewer texts covering216 responses, and all4 malformed main answers were
manually checked. Export/analysis/reporting sent zero new API requests. The
seven-page English main PDF has a211-word abstract, required ethics and AI-use
statements, a warning-free Tectonic0.16.9 cached build, and visually checked
title/results/appendix. A later shared-source pilot rebuild was restored to the
exact previously published PDF; its README now pins historical presentation
source3832913. No pilot observation or published snapshot was replaced.

Coordinator and peer read-only reviews found no blocking claim, provenance,
privacy or denominator issue. Both repeated the public campaign and evidence
checks; the coordinator additionally checked source/private-public equality and
the final PDF. Public material is confined to this study's subtree, with immutable
acquisition inventory87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e.
Existing draft PR#4 remains the publication route; no self-merge or competition
submission was performed. Complete no-network reproduction commands are in
`reports/main/README.md` and `results/live-main-2026-11-08/README.md`.

## 2026-11-09 — Completed-main release published in the existing PR

Fetched origin, reviewed the staged scope/content and privacy markers, verified
append-only history and the unchanged historical pilot PDF, and committed only
31 owned study files as `7c7c7ecdc422bb384cf588adc587971e1af46f6c`
(Report the frozen held-out evaluation and complete audited campaign). The
normal fast-forward push to `study/wrong-goal-proof-live-v1` succeeded; live
PR#4 reports that exact release commit and remains open. No force-push, direct
main update, self-merge or competition submission occurred.

The final seven-page main PDF has89617 bytes and SHA256
`6138a80c1aad371d8e7669a0202757e98b9084c344cfca8af1640e82578b0b8d`.
PDF text privacy, required appendices, all14 exported-file hashes and exact
approved GO equality passed. All29 staged text files passed the private-marker
scan; the two additional staged files are the reviewed PDF report and figure.
Frozen acquisition inventory remains87e58d63f04fad074d3793527964d6431521067d399f205616307f558257960e.
The shared project check passed11 contests/16 TickTick links; shared tracking
and merge remain the coordinator's responsibility. No additional API request
was made during publication.

## 2026-11-09 — New standalone reader edition; unchanged scientific evidence

After the completed empirical PR #4 was merged as
`755e51475e343825c67e142cbbe34aff2f22f9b3`, a separately authorized editorial phase
started from clean main `7e2780c1357dcb0ce14b749caf222fd1080bad06` on
`study/wrong-goal-proof-reader-report`. No prior commit was rewritten and no
new model request, secret access, purchase or competition submission occurred.

Wrote a fresh standalone English report in `reports/reader/`, rather than
overwriting the historical pilot or main manuscripts. The six-page PDF includes
references and the mandatory ethics/limitations appendix, a 209-word abstract,
clickable repository URL before the abstract, separate pilot/main accounting,
all seven main condition rows and both paired contrasts with wide intervals.
The visible-original baseline, null findings, four natural format-related
failures, two unknown-cost attempts and study-only budget remain explicit.
It claims neither general safety, presentation equivalence, label benefit nor
a new mathematical equivalence criterion. Human author review is still pending.

Two actual records were selected after the run for clarity: the unique shortest
combined rendered formulas among planted and equivalent cases. The report shows
ordinary PASS condition B for `holdout-fault-019` and `holdout-equivalent-019`.
The reversed-implication example has a valid candidate SAFE certificate but an
original counterexample at all-false inputs; the model correctly returned UNSAFE.
The redundant-condition example preserves both open functions and was correctly
answered SAFE. Exact JSON pointers, source-file hashes, quotes and all 16 states
are in `report-data.json`. A separate literal interpretation and both frozen
evaluators agree on every state; all six recorded example conditions are bound
to their actual original task, candidate, certificate and visible answer.

Actual Python 3.14.6 checks: 171 frozen scientific/acquisition tests PASS in
21.510 s, 28 existing reporting/accounting tests PASS in 0.300 s, and 12 new
reader-binding tests PASS in 0.062 s. The full public campaign audit and both
empty false-guarantee evidence checks passed. The reader checker repeated both
saved analyses and protected 91 old files byte for byte, including all old
PDFs/TeX, data and scientific source. These checks sent zero new model requests;
310 requests in audit output refer only to historical acquisition.

Cached Tectonic 0.16.9 produced a warning-free 60,988-byte PDF, SHA256
`44c513f94263a077c1a2865ab82bd1ad2d52c395d3cd52cde42a40ac532108c9`.
All six pages were rendered and visually inspected; updated pages were checked
again. Repository annotations, abstract length, standalone scope and extracted
text privacy checks passed. The current official template was read fully and
both cited papers' exact version, author metadata and abstracts were rechecked.

Reorganized only owned study navigation. Earlier detailed guide text is retained
in `ENGINEERING_GUIDE.md` and `reports/TOOLS.md`; historical plan prose is labeled
as historical, not rewritten, and this history remains append-only. Read-only
integration review independently confirmed examples, PDF, checker and 12 tests
without a blocker. Peer source review and a separate editorial PR remain pending
at this checkpoint; no self-merge or direct main push occurred.

## 2026-11-09 — Reader peer review closed; terminology clarified

Read-only peer review independently reran the source-bound checker, inspected the
full manuscript/helper and exact saved examples, and found no blocking issue.
Its small terminology suggestion was accepted: the equivalent example repeats
an allowed-state condition C, rather than changing the required property Q.
The abstract now says "redundant condition"; formulas, data, numerical results,
selection rule and generated tables are unchanged.

The rebuilt final reader PDF remains six pages with a 209-word abstract and
zero TeX warnings. It is 60,961 bytes, SHA256
`c8bf9d451609a49e2f1a159a24a9d4a9adf58d57b4eeb6f616c259932c7e9d78`.
The earlier draft hash above remains a dated checkpoint, not the current PDF.
All eight edited/new navigation documents have resolving relative file links;
the relocated guides preserve their original bodies exactly. Historical plan
scientific text and the full earlier history prefix remain unchanged. Publication
will use a separate editorial PR; no self-merge or competition submission is made.

## 2026-11-09 — Reader release published as separate PR #5

Fetched origin before publication, reviewed the 19 staged paths and content,
and committed only this study's editorial files as
`de25ca8170915c345dbbd0387bf0ee857faa0b5a`
(Add a standalone reader report and simplify study navigation). Staged whitespace,
owned-scope and text privacy checks passed. The ordinary push created
`study/wrong-goal-proof-reader-report`; no force-push or direct main push occurred.
An exact-branch PR lookup returned no existing PR before creating the ready,
non-draft [PR #5](https://github.com/RuslansAleksejevs/boundary-conditions/pull/5).
It is open, not integrated, at the 2026-11-09T05:17:50Z publication checkpoint.

The final six-page, 60,961-byte PDF and its hash above are unchanged. The final
reader-binding rerun passed all 12 tests in 0.059 s and the no-network checker
again preserved 91 old files, replayed both analyses and verified all six example
conditions. The final terminology-only edits on pages one and four were visually
checked. This is additional reporting verification, not new model evidence.
The coordinator and peer received the PR, release commit, test results and final
PDF hash. Integration and human author review remain pending; no self-merge,
new inference or competition submission occurred.
