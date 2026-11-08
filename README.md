# Boundary Conditions

**What survives when one agent hands work to another?**

Two small, controlled studies of trust and meaning at agent boundaries.
Built for the [Swarm Alignment Hackathon 2026](https://apartresearch.com/sprints/swarm-alignment-2026).

> **Research status — 7 November 2026:** study designs prepared; two isolated
> implementation workstreams have started. No model experiments or measured findings yet.

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

### Verified, but What?

A translator formalizes a small Boolean contract. An exact checker certifies
that formalization. A separate reviewer must answer the original question.
We distinguish naturally occurring drift from deliberately injected changes,
then compare different presentations of the same valid certificate.

Primary track: **The Science of Agent Networks**. Also relevant to
**Multi-Agent Oversight and Control**.

## Research discipline

- Measure effects with code: state transitions and exhaustive finite checks.
- Separate development cases from a frozen evaluation set.
- Report utility, abstentions, missing runs, cost, and uncertainty—not just failures.
- Distinguish model behavior from injected faults and guarantees enforced by code.
- Keep the two studies' datasets and claims separate; disclose shared infrastructure.
- Treat related work as prior art, not as results reproduced here.

See the [shared protocol](docs/PROTOCOL.md), [related work](docs/RELATED_WORK.md),
and [research log](RESEARCH_LOG.md).

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

Runnable code, exact environment instructions, and measured results will be added
as they exist. There are no experiment commands or performance claims to reproduce yet.

## Scope and safety

The planned environments use synthetic records, in-memory tools, and finite
Boolean formulas. They do not target live services, expose real credentials,
or perform real-world unauthorized actions. Toy-environment results will not
establish the security of production systems or arbitrary mathematical agents.

This repository contains the public research record only. Private coordination
notes, personal context, credentials, and unreviewed raw logs are excluded.

## Reuse

No license has been selected yet. Public visibility does not grant an open-source
license. References retain their respective authorship and terms.