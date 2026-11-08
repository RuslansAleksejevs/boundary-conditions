# Related work and claim boundaries

Reviewed 7 November 2026. This is a focused reading list, not a systematic review.
The reported findings belong to their authors; we have not reproduced them.
No priority or novelty claim is established by this list.

## Study A: summary laundering

### Can CaMeLs Talk? Securing Multi-Agent Systems Against Indirect Prompt Injection Attacks

[arXiv:2610.05640v1](https://arxiv.org/abs/2610.05640v1)

The paper already demonstrates how untrusted content can cross an agent boundary
as trusted input, including a summarization handoff. Its multi-CaMeL protocol
preserves the distinction between instructions and data across agents.

Our candidate contribution is narrower: a paired factorial experiment separating
text transformation from the source description shown to a receiver, without
changing actual instruction privileges. We are not claiming to discover
provenance laundering or to reproduce multi-CaMeL.

Reading scope: abstract, relevant parts of the introduction and Section III,
and Section VI on limitations.

### StateFence: Task-State Protection Against Evidence-Chain Contamination in Blue-Team LLM Agents

[arXiv:2611.02605v1](https://arxiv.org/abs/2611.02605v1)

StateFence examines how untrusted evidence contaminates intermediate task state
in security-operations workflows. It also makes the utility cost of filtering
important: suspicious text can contain information the task needs.

Our planned environment is not a SOC benchmark. The relevant lesson is to
measure actual state changes and useful completion together, rather than only
the disappearance of suspicious strings.

Reading scope: abstract, introduction, threat model, and limitations.

## Study B: wrong-goal proof

### SemantEq: Faithful Bidirectional Equivalence of Formal Statements

[arXiv:2610.32919v1](https://arxiv.org/abs/2610.32919v1)

A valid proof does not establish that its statement faithfully represents the
intended task. Even unrestricted bidirectional implication is too permissive
for closed theorems: independently provable statements can imply one another
without expressing the same mathematical claim.

We do not offer a general solution to faithful autoformalization. Our finite
contract fixes atom meanings, an admissible-state function C, and an obligation
Q. We compare these as open Boolean functions and separately check the final
claim about the original contract.

Reading scope: abstract, introduction, and relevant parts of Sections 2–4.

### Beyond LLM Judge: Mechanical Verification for Agentic Autoformalization

[arXiv:2610.20573v2](https://arxiv.org/abs/2610.20573v2)

This work combines semantic review with mechanical numerical and vacuity checks
and reports defects missed by model-based judges. The insufficiency of checking
only the proof is established prior work.

Our proposed experiment instead holds the original task, candidate statement,
and valid local certificate fixed while changing how the certificate's scope
is presented to a downstream reviewer. Exact counterexamples determine false
claims about the original finite contract.

Reading scope: abstract and relevant methods, experiments, case studies, and
conclusion in Sections 3, 5, 6, and 7.

## What we are not claiming

Provenance labels, exact finite verification, and permission gates are known
engineering tools. A hard gate's guaranteed rejection in our toy environment
is not a new empirical security result. Any contribution must come from the
controlled comparisons and actual evidence produced by these studies.