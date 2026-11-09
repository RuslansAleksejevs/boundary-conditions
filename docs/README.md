# Reading guide

Start with the [repository overview](../README.md). You do not need to read the
engineering log to understand either question or its result.

## Read the studies

| Study | Short report | Plain-language guide | Saved evidence |
| --- | --- | --- | --- |
| Prompt Injection at Agent Handoffs: The Second-Hand Instruction Problem | [3-page PDF](../reports/prompt-injection-at-agent-handoffs-the-second-hand-instruction-problem.pdf) | [Guide](../studies/summary-laundering/README.md) | [Main data](../studies/summary-laundering/results/main-2026-11-09/README.md) |
| A Certificate Is Not the Answer | [3-page PDF](../reports/a-certificate-is-not-the-answer.pdf) | [Guide](../studies/wrong-goal-proof/README.md) | [Pilot and main data](../studies/wrong-goal-proof/results/live-main-2026-11-08/README.md) |

The [final reports](../reports/README.md) are separate papers. Each includes its own question, method,
tables, worked examples, limitations and references. Their examples illustrate
saved observations; they do not add new experiments or replace the full dataset.

## Follow or check the work

| If you want to… | Open… |
| --- | --- |
| See what happened and when | [Timeline](../TIMELINE.md) |
| Check the published results without paying for API calls | [Reproduction guide](REPRODUCE.md) |
| Understand the closest prior work | [Related work](RELATED_WORK.md) |
| See the model settings, funding and actual expenditure | [Execution budget](EXECUTION_BUDGET.md) |
| Inspect the detailed original record | [Lab log](../RESEARCH_LOG.md) |
| Find LaTeX sources, file hashes and final PDF checks | [Final report package](../reports/README.md) |
| Distinguish current papers from old versions | [Report archive](ARCHIVE.md) |

## Original plans and historical records

These files are kept because the order of decisions matters. A statement such
as “no model calls yet” describes its dated checkpoint, not today's status.

- [Shared protocol](PROTOCOL.md): scoring, uncertainty and evidence standards.
- [Original execution plan](NEXT_EXPERIMENTS.md): pilot gates and fixed main sizes.
- [Operational amendment](OPERATIONAL_AMENDMENTS.md): how the interrupted pilot
  was continued without repeating observed answers or relaxing its quality gate.
- [Summary study history](../studies/summary-laundering/HISTORY.md) and
  [certificate study history](../studies/wrong-goal-proof/HISTORY.md): detailed
  workstream records, including earlier drafts and failed development checks.

The first full reports and pilot-only PDFs remain in their original locations.
They are historical snapshots, not competing “latest” reports. The
[archive](ARCHIVE.md) identifies them. Scientific source files, original result files and old PDFs are
preserved; shorter writing does not mean silently changing the evidence.

## A few terms used in the records

**Pilot:** a small development run that checks the interface and ordinary task
completion before the main evaluation.

**Frozen evaluation:** cases, settings and analysis fixed before their responses
were collected. This was a local record, not a registry preregistration.

**Null result:** the planned comparison did not show the target effect. It does
not show that the true effect must be zero.

**Replay:** run the saved responses through the same deterministic checks.
It needs no model access and is not a new empirical replication.

**Reserve:** a cautious bookkeeping allowance for an unresolved charge. It is
not additional money known to have been spent.
