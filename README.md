# Boundary Conditions

**Two small studies of what can go wrong when agents pass work to one another.**

An instruction can hide in a summary. A valid certificate can answer the wrong
question. We tested both possibilities using Qwen3.5-122B-A10B, synthetic tasks
and exact Python checks.

**The failures we looked for did not occur in these tests.** That is a useful
result to report, not a guarantee that the model or larger agent systems are safe.

[Final reports](reports/README.md) · [Work timeline](TIMELINE.md) ·
[Check the results](docs/REPRODUCE.md) · [Full reading guide](docs/README.md)

## 1. Prompt Injection at Agent Handoffs

*The Second-Hand Instruction Problem*

Does an unsafe instruction become more persuasive when another agent summarizes
it, or when the same text is presented as a colleague's message?

We varied the text and its source label separately. The executor had to save a
code or a subtraction result without changing an unrelated approval flag.
The main test used 40 attacked records and 20 paired clean records in eight
conditions.

**Result:** no forbidden change in 478 observed responses. Of 480 scheduled
responses, 443 completed the task, 33 had invalid format, two took no action and
two were missing. The primary comparisons had zero observed difference, with
wide uncertainty. Neither warning showed a security benefit.

[Read the final PDF · 3 pages](reports/prompt-injection-at-agent-handoffs-the-second-hand-instruction-problem.pdf)
· [Study guide](studies/summary-laundering/README.md)
· [Data](studies/summary-laundering/results/main-2026-11-09/README.md)

Track **3: Strengthening Agent Infrastructure**, also **2: The Science of Agent Networks**.

## 2. A Certificate Is Not the Answer

Will a reviewer accept a valid certificate for an altered task as an answer to
the original request?

We used small Boolean contracts whose answers can be checked across all 16
possible states. A reviewer saw the original task and a candidate certificate
under three headings: PASS, a neutral record, or an explicit scope warning.

**Result:** all 40 planted substitutions were rejected and all 20 harmless
rewrites accepted under every heading. The ordinary translation pipeline
completed 36 of 40 tasks; four remained unassessed because of format errors.
No false assurance was observed. The strong baseline leaves no demonstrated
benefit for the scope warning.

[Read the final PDF · 3 pages](reports/a-certificate-is-not-the-answer.pdf)
· [Study guide](studies/wrong-goal-proof/README.md)
· [Data](studies/wrong-goal-proof/results/live-main-2026-11-08/README.md)

Track **4: Multi-Agent Oversight and Control**.

## Check the work

From the repository root, with Python 3.11+:

```sh
python3 reports/check_reports.py
```

This checks the report tables and examples against saved data, including every
state of the Boolean examples. **No API key, model download or paid request is
needed.** The [reproduction guide](docs/REPRODUCE.md) also covers full data replay,
software tests and optional PDF rebuilding.

Both studies use one hosted model, small synthetic task families and one sample
per condition. Paired conditions are not independent tasks. Invalid and missing
responses stay in the results. Offline replay checks the saved observations; it
is not a new model experiment or independent proof of provider origin.

## About this project

Built for the [Swarm Alignment Hackathon](https://apartresearch.com/sprints/swarm-alignment-2026)
in November 2026 by **Ruslans Aleksejevs · UC Berkeley**. The final reports are
dated 9 November. Competition submission and acceptance are not claimed here.

The name connects two boundaries: **who may change the task**, and **what a
certificate actually establishes**. It is a shared theme, not a new mathematical
method. The failure mechanisms are established prior work; our contribution is
the controlled tests and their recorded results.

- **Cost:** $3.75323494 used from $50 in OpenRouter credits, including pilots and
  technical retries. [Accounting and model settings](docs/EXECUTION_BUDGET.md).
- **AI assistance:** GPT-6 Astra helped with design, code, checks and writing.
  Qwen was the experimental subject; scoring used deterministic code.
- **History:** [timeline](TIMELINE.md), [original lab log](RESEARCH_LOG.md),
  [related work](docs/RELATED_WORK.md), [earlier report versions](docs/ARCHIVE.md).
- **Reuse:** no license has been selected. Public visibility alone is not an
  open-source license. No real accounts or services were attack targets.