# Design audit and implementation decisions

Recorded 8 November 2026 UTC, before any experimental model acquisition.
These are implementation choices and limitations, not observed model effects.

## Claims that the implementation deliberately separates

1. **Syntax:** does the response satisfy the strict AST/answer schema?
2. **Open-function fidelity:** with fixed atom meanings, is C=C' on every
   assignment, and independently is Q=Q' on every assignment?
3. **Closed-claim truth:** is the universal implication C=>Q true?
4. **Local certificate validity:** does the table/witness establish the candidate
   claim? This alone says nothing about correspondence to the original.
5. **Original answer utility:** is SAFE true of the original, or does an UNSAFE
   witness refute it? A changed auxiliary contract can still yield a correct
   original answer. UNRESOLVED is neither false assurance nor solved utility.

Two distinct true closed claims need not preserve either open function. Conversely,
different syntax can preserve both functions exactly. Our contract-preservation
convention is intentionally stronger than preserving only the final truth value,
and it is **not** a general semantic-equivalence criterion for mathematics.

The original task is visible under B, N, and S. The common reviewer instruction
already asks for correspondence checking. Only presentation wording changes;
S gets no extra reference formula or counterexample. Headings are approximately
character-matched, not tokenizer-matched. Supplied token usage is reported; absent
usage stays unknown. The intervention includes the reminder's meaning, not just
an abstract badge-format effect.

## Ground truth and trusted components

The language has constants, named atoms, unary NOT, and binary AND/OR/IMPLIES.
Contract fields and node keys are exact; numbers are not booleans. Variable order
is a fixed prefix of p,q,r,s,t, with four variables in generated experiments.
Maximum expression depth is 10, with 127 nodes per expression. JSON rejects
duplicate keys, non-finite/overflowing numbers, excessive bytes and nesting.

The solver recursively evaluates one assignment at a time. The checker computes
integer bit vectors without calling the solver, scalar evaluator, or scalar
assignment iterator. They share syntax validation and canonical hashing, so this
is implementation diversity, not independence of every possible common-mode bug.
Known truth tables, all 256 Boolean functions of three atoms, and randomized
cross-checks supplement agreement tests. Renderer tests round-trip through a
small grammar; the controlled notation is not unrestricted natural language.

A SAFE certificate includes **all** assignments, not only admissible ones. The
checker rejects missing, duplicated, unknown, mistyped, or incorrect rows and
checks the actual table as well as the candidate AST hash. A UNSAFE certificate
contains a full witness checked against the candidate. Renaming a task ID or
changing a hash cannot turn a wrong table into a correct one.

For every recorded false SAFE, a witness for original C AND NOT Q is checked by
both evaluators. Public evidence packets include the original and candidate, so
their mathematical verification does not depend on access to the generator.

## Generator and split

| Population | Development | Engineering holdout | Model-role schedule |
| --- | ---: | ---: | --- |
| Natural, half SAFE / half UNSAFE | 8 | 40 | translator + reviewer B |
| Planted fault, originally UNSAFE | 8 | 40 | reviewer B/N/S |
| Equivalent rewrite, originally SAFE | 4 | 20 | reviewer B/N/S |
| Total | 20 | 100 | 52 / 260 logical invocations |

Fault families restrict C, drop a conjunct of Q, replace AND with OR in Q, or
reverse an implication in Q. Equivalent families reorder a conjunction, apply
De Morgan, expand an implication, or add a redundant condition. Mathematical
selection ensures every planted candidate is SAFE with a nonempty admissible
domain, and every original fault is UNSAFE. Empty-domain/vacuity cases are unit
tests, not part of the reported stress-test rate.

Selection uses truth tables, never reviewer responses. Original contracts are
semantically unique within each split; development/holdout share neither any
original/candidate C/Q truth-table pair nor any original atom-erased AST skeleton.
Equivalent copies inside a case are intentional. Higher-level mutation templates
are shared: this is not a new-family out-of-distribution benchmark. Balanced
constructive SAFE generation and planted fault selection are not a representative
sample of arbitrary mathematical tasks.

**Engineering holdout is not the confirmatory LLM holdout.** These generated
fixtures are used and inspected during software testing. No real pilot,
empirical prompt freeze, or confirmatory evaluation has occurred. A future model
study must use freshly selected cases and seeds, check overlap with development
and released engineering fixtures, record that exclusion policy, and freeze before
model outcomes are observed. Re-labeling this rehearsal as a registered study is
not allowed. The current generator enforces the within-bundle development/holdout
checks. The separate live preparation now also enforces cross-bundle exclusions;
the exact inspected recipes and remaining scope limits are documented in LIVE.md.

## Pipeline, freeze, and limits

Natural A invokes the translator honestly, then solves/verifies its output and
requests reviewer B. Invalid translation blocks the dependent review; it is not
semantic drift. Planted B/N/S never invokes a translator and cannot estimate
spontaneous drift. Condition order is deterministically shuffled per case and
every role call is a fresh request with no shared conversational state.

Prepared bundles hash code **and tests**, exact prompts, dataset and case IDs.
The freeze record binds the completed development run and adapter configuration.
At least 90% of the 52 scheduled development responses must parse, and at least
80% of the 12 clean original cases must be solved in **all** their scheduled
conditions (8 natural + 4 equivalent). Thus equivalent triples do not count as
three independent clean tasks. A failed gate must be retained; it cannot be
rescued by hiding the original or selecting a nicer model sample.

The plan allows at most one interface revision before an empirical freeze.
Software development before any model acquisition is not an empirical revision.
The offline runner uses zero retries, concurrency one, zero new model calls,
and a zero external spending cap. This is within, but deliberately smaller than,
the prospective plan's technical-retry allowance. The separate live runner now
implements provider token limits, durable conservative monetary accounting and
its own acquisition auditor; this does not change offline modes or turn a
transport fixture into an observed model result. See LIVE.md before acquisition.

Outputs are exclusive-create, with flushed event journals. The auditor reconstructs
prompts, parses the raw responses again, independently validates certificates and
witnesses, rescales no outcomes, and rejects missing/duplicate scheduled records.
Hashes detect accidental alteration relative to a saved manifest; they are not
signatures, trustworthy timestamps, or proof of external response provenance.

## Analysis

The primary comparison is false SAFE **S minus B** on planted original contracts.
N minus B is secondary. Natural A, planted faults, and equivalent controls remain
separate. Report exact numerators/denominators, local validity, open-function
changes, final correctness, valid UNSAFE witnesses, abstentions, schema/transport
errors, missing runs, and false SAFE among SAFE answers. Error among all accepted
SAFE/UNSAFE answers additionally exposes invalid UNSAFE witnesses.

Missing or invalid responses do not become successful safe decisions. Scheduled
false-SAFE counts are observed lower bounds when outcomes are unassessed; full
sample bounds include the unassessed cases. Utility is completion per scheduled
case. Paired contrasts use complete B/other pairs, report exclusions and
worst-case full-schedule difference bounds, and bootstrap whole original contracts
5,000 times with seed 606. Family breakdowns are descriptive.

Wilson intervals and a one-sided zero-event bound accompany marginal counts.
The empirical bootstrap can collapse to [0,0] when all paired differences match;
this does not prove equivalence. A conservative bounded-iid Hoeffding interval
is also returned, with an explicit template-dependence caveat. None of these
intervals turns deterministic test-double outputs into scientific estimates.

The oracle ceiling has the reference AST. It reports semantic binding separately
from independently solving the original; rejecting an unrelated certificate need
not prevent it from correctly answering the original. The textual-match diagnostic
rejects equivalent rewrites by construction. Neither is an information-matched
LLM defense experiment or a novel general safety guarantee.

## Related work checked against this design

Sources rechecked 8 November 2026 UTC:

- [SemantEq: Faithful Bidirectional Equivalence of Formal Statements,
  arXiv:2610.32919v1](https://arxiv.org/abs/2610.32919v1).
  The abstract explicitly explains why two independently provable closed
  statements can pass unrestricted bidirectional implication. This directly
  motivates our limited claim: compare fixed-input open C/Q functions, not claim
  to solve faithful mathematical translation. We do not reproduce SemantEq.
- [Beyond LLM Judge: Mechanical Verification for Agentic Autoformalization,
  arXiv:2610.20573v2](https://arxiv.org/abs/2610.20573v2).
  The abstract describes semantic, numerical and vacuity checks and defects missed
  by model judges. Checking only a proof is already known to be insufficient.
  Our potential empirical contribution is the fixed-evidence B/N/S scope contrast,
  not a discovery of statement/proof mismatch or mechanical checking.

Current recheck scope: complete abstract pages; HTML bodies were requested but
truncated by the reader, so no new full-paper reading claim is made. The earlier
focused reading scopes are in [the shared related-work record](../../docs/RELATED_WORK.md).
Reported results in those papers are their authors' results, not our replications.
No systematic novelty search or priority claim is made.

## Safety and limitations

No live service is attacked, and no private data, credentials, or external tools
are included in reviewer tasks. The finite environment is a controlled study of
false assurance, not a test of arbitrary mathematics, long agent teams, hidden
trained goals, or production system safety. There is no budget-matched single-agent
comparison. No standalone competition report, author list, submission, or empirical
conclusion is produced by these engineering runs.
