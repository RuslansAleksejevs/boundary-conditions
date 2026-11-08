# Shared research protocol

**Status:** design draft, 7 November 2026. No experiments have run.
The study-specific plans define their hypotheses and controls. This document
sets the common standards for execution, records, and interpretation.

## Sequence

1. Test the environment and scorer without an LLM.
2. Run the bounded development pilot.
3. Resolve interface problems within the declared revision budget.
4. Freeze prompts, generators, model configuration, cases, and analysis.
5. Run the evaluation set once under that frozen protocol.
6. Audit traces, quantify uncertainty, and report every scheduled condition.

This is a prospective working plan, not a claim of registered or completed research.
Changes after evaluation begins must be dated and labeled exploratory. A smaller
evaluation set may be selected before observing its outcomes, with reduced
precision disclosed. A promising pilot does not guarantee a positive main result.

## What to freeze

Each study needs a manifest containing:

- Code revision and dataset/generator hashes.
- Development/evaluation split, scenario identifiers, and random seeds.
- Exact provider, model identifier/version, sampling and reasoning settings.
- Prompts, tool schemas, role boundaries, context limits, and output limits.
- Number of calls, permitted retries, concurrency, and monetary stop.
- Primary outcomes, comparisons, exclusions, and analysis code version.

If an API does not support a seed or a pinned model version, record that fact.
Temperature zero is not a reproducibility guarantee. Never put credentials in
the manifest, commands, prompts, or logs intended for publication.

## Proposed model-call budget

| Study | Pilot | Evaluation | Total |
| --- | ---: | ---: | ---: |
| Summary laundering | 108 | 540 | 648 |
| Wrong-goal proof | 52 | 260 | 312 |
| **Combined** | **160** | **800** | **960** |

These are planned counts, not calls already made or permission to incur costs.
One model and one sample per condition are sufficient for the core design.
A second model, repeated samples, adaptive attack search, and longer chains
are optional extensions requiring a separately recorded budget.

Allow one identical retry after a transport failure, with total retry overhead
capped at 5% of the planned calls. A refusal or an unhelpful model answer is not
a transport failure and must not be retried until a preferred outcome appears.

Record input, output, and billable reasoning tokens; caching; latency; and the
applicable provider prices. An unknown cost is not zero. Hard request and spending
limits must be set before execution, with dependent stages kept sequential.

## Records and analysis

Keep enough information to reconstruct each case: frozen inputs, model outputs,
parsed actions, tool events, certificates, state changes, scorer output, request
metadata, and technical errors. Preserve original records; append corrections.

The sampling unit is the original scenario or contract. Resampling must retain
all paired conditions together. Repeated tool calls and transformed copies are
not additional independent samples. Report raw counts, paired differences, and
confidence intervals. Template dependence limits generalization.

Report scheduled, attempted, completed, invalid, and missing runs. Do not count
timeouts as safe successes. Include task completion and abstention rates so
that rejecting everything cannot masquerade as a useful defense.

Small samples mainly detect large effects. Zero failures in 40 independent
cases still has a one-sided 95% binomial upper bound of approximately 7.2%.
Do not treat narrow test coverage as a universal safety guarantee.

## Publication and maintenance

- Keep plans, actual runs, and conclusions visibly distinct.
- Publish reviewed synthetic examples and sanitized records only.
- Update the research log at meaningful milestones, including failures and nulls.
- Use focused English commits and preserve reproducible evaluation revisions.
- Attribute preexisting work and shared infrastructure explicitly.
- Do not count the same experimental result as an independent finding in both studies.
- Review staged files for secrets and personal material before every public push.

No background publication or monitoring automation is part of this repository.
Competition submission is separate from maintaining the public research record.