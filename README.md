# Boundary Conditions

**What survives when one agent hands work to another?**

Two small, controlled studies of trust and meaning at agent boundaries.
Built for the [Swarm Alignment Hackathon 2026](https://apartresearch.com/sprints/swarm-alignment-2026).

> **Completed — 9 November 2026:** Both frozen real-model evaluations, audited
> datasets and English reports are integrated through reviewed PRs
> [#3](https://github.com/RuslansAleksejevs/boundary-conditions/pull/3) and
> [#4](https://github.com/RuslansAleksejevs/boundary-conditions/pull/4).
> Neither target failure was observed in this bounded Qwen/Alibaba setting.
> Invalid and missing responses remain visible; nulls do not establish general
> safety or equivalence. Account-confirmed API expenditure is **$3.75 of $50**,
> including development and technical retries. Human author review is pending;
> **neither report has been submitted to the competition**.

## Two boundaries

An external document becomes a colleague's summary. A formal statement becomes
a checked certificate. In both cases, a handoff may carry more authority than
the evidence warrants.

| Study | The boundary | The question |
| --- | --- | --- |
| [Who Said That?](studies/summary-laundering/PLAN.md) | External data → agent handoff | Does risk come from rewriting the text, from how its source is presented, or both? |
| [Verified, but What?](studies/wrong-goal-proof/PLAN.md) | Original contract → checked statement | Does a correct local certificate lead a reviewer to endorse the wrong original claim? |

The name is a double reference: **trust boundaries** in software systems and
the **conditions under which a mathematical claim holds**. Neither study assumes
that a failure will occur.

### Who Said That?

A summarizer reads an untrusted synthetic note. An executor performs a legitimate
task using a mock tool. We replay the same text with different source descriptions,
separately vary original text, verbatim extraction, and summarization, and measure
actual unauthorized state changes alongside useful task completion.

Primary track: **Strengthening Agent Infrastructure**. Also relevant to
**Multi-Agent Oversight and Control**.

**Completed result:** no unauthorized state change in 478 observed executor
cases, with 443/480 scheduled cases completed correctly. The 33 invalid and two
missing responses are not counted as successful safe completion. A strict
action interface rejects invalid batches, so the zero is a result of the tested
model-and-tool pipeline, not a general claim about model intentions or safety.
Read the [report guide](studies/summary-laundering/report/README.md),
[main PDF](studies/summary-laundering/report/main-report.pdf), and
[replayable results](studies/summary-laundering/results/main-2026-11-09/README.md).

### Verified, but What?

A translator formalizes a small Boolean contract. An exact checker certifies
that formalization. A separate reviewer must answer the original question.
We distinguish naturally occurring drift from deliberately injected changes,
then compare different presentations of the same valid certificate.

Primary track: **The Science of Agent Networks**. Also relevant to
**Multi-Agent Oversight and Control**.

**Completed result:** all three certificate presentations correctly handled all
40 planted substitutions and 20 equivalent controls. Natural-task completion
was 36/40; four malformed responses remain unassessed. Read the
[full report](studies/wrong-goal-proof/reports/main/README.md),
[seven-page PDF](studies/wrong-goal-proof/reports/main/main-report.pdf), and
[replayable campaign](studies/wrong-goal-proof/results/live-main-2026-11-08/README.md).

## Research discipline

- Measure effects with code: state transitions and exhaustive finite checks.
- Separate development cases from a frozen evaluation set.
- Report utility, abstentions, missing runs, cost, and uncertainty—not just failures.
- Distinguish model behavior from injected faults and guarantees enforced by code.
- Keep the two studies' datasets and claims separate; disclose shared infrastructure.
- Treat related work as prior art, not as results reproduced here.

See the [shared protocol](docs/PROTOCOL.md), [related work](docs/RELATED_WORK.md),
and [research log](RESEARCH_LOG.md). The [execution budget](docs/EXECUTION_BUDGET.md)
records funding, model settings, spending stops, and data handling.

## Repository map

```text
studies/
  summary-laundering/   Study A: text, provenance, and unauthorized actions
  wrong-goal-proof/     Study B: contracts, certificates, and false assurance
docs/
  PROTOCOL.md          Shared evaluation and reporting rules
  RELATED_WORK.md      Sources, overlap, and limits of our claims
RESEARCH_LOG.md        Dated milestones, including negative results
```

Runnable harnesses and engineering records are available for
[Study A](studies/summary-laundering/README.md) and
[Study B](studies/wrong-goal-proof/README.md). Each records its actual tests and
reproduction commands. Software tests and deterministic CLI rehearsals do not
constitute observations of model behavior.
The [original execution plan](docs/NEXT_EXPERIMENTS.md) and
[operational amendment](docs/OPERATIONAL_AMENDMENTS.md) preserve the prospective
schedule, interrupted pilot, missing cases and paced continuation. Historical
development snapshots are kept separate from the completed held-out evaluations.
After both merges, **365 local tests passed** and both public-data checks passed
again without API requests. No GitHub CI or independent provider attestation is
claimed.

## Scope and safety

The tested environments use synthetic records, in-memory tools, and finite
Boolean formulas. They do not target live services, expose real credentials,
or perform real-world unauthorized actions. Toy-environment results do not
establish the security of production systems or arbitrary mathematical agents.

This repository contains the public research record only. Private coordination
notes, personal context, credentials, and unreviewed raw logs are excluded.

## Reuse

No license has been selected yet. Public visibility does not grant an open-source
license. References retain their respective authorship and terms.