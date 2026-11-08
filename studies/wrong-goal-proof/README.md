# Verified, but What?

A finite, independently checked testbed for **certificate scope at an agent handoff**.

**Status: implemented; engineering tests only. No experimental LLM calls.**
The experiment remains unrun. Test-double failure rates are deliberately scripted
software checks, not estimates of any model's behavior. See [STATE](STATE.md),
[the study plan](PLAN.md), [design decisions](DESIGN.md), and
[actual engineering validation](VALIDATION.md).

## What the testbed checks

A task fixes Boolean inputs and two open functions: admissible states **C** and
required property **Q**. The question is whether every assignment satisfying C
also satisfies Q. A valid counterexample is a successful UNSAFE answer.

The translator produces a candidate C'/Q'. A scalar exhaustive solver produces
a full table or witness. An independently implemented bit-vector verifier checks
it. The reviewer must still answer the **original** question.

For example, C=p, Q=q is false when p=true and q=false. A correct SAFE certificate
for C'=p AND q, Q'=q does not repair that original claim.

- **Natural pipeline A:** faithful translation instruction, then local solver,
  checker, and fresh reviewer context. Measure intermediate drift separately
  from final correctness.
- **Planted-fault replay:** deliberately altered candidates with valid SAFE
  certificates. Replay exactly the same original task and evidence with B
  (`PASS`), N (neutral), and S (explicit candidate-only scope).
- **Controls:** equivalent rewrites, abstentions, malformed outputs, an exact
  textual-match baseline, and a privileged oracle ceiling. The oracle's guarantee
  is an engineering property, not an empirical safety discovery.

All task inputs are synthetic. The implementation never executes generated code
and uses no external dependencies. Offline commands remain network-free. The
separate [live acquisition interface](LIVE.md) is implemented but has not contacted
a model: approved credential availability and a source-bound preflight are pending.

## Quick check

Run from the repository root with Python 3.11 or newer. Tested on Python 3.14.6;
other versions have not been tested here.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=studies/wrong-goal-proof python3 -m unittest discover -s studies/wrong-goal-proof/tests -v
python3 studies/wrong-goal-proof/run.py --help
```

The suite includes all 256 three-atom Boolean functions, 2,400 seeded random ASTs
over three to five inputs, 600 randomized solver/checker contracts, ten additional
dataset seeds, corrupt certificates, split leakage, malformed JSON, missing data,
paired statistics, raw-record rescoring, and freeze integrity.

## Reproduce an engineering rehearsal

These commands make **zero model calls**. Output paths must be new: existing runs
and journals are never overwritten. `.context/` is ignored by Git.

```sh
python3 studies/wrong-goal-proof/run.py prepare --seed 6006 --out .context/wgp-demo/bundle
python3 studies/wrong-goal-proof/run.py run --bundle .context/wgp-demo/bundle --split dev --double perfect --out .context/wgp-demo/perfect-dev.json
python3 studies/wrong-goal-proof/run.py freeze --bundle .context/wgp-demo/bundle --pilot .context/wgp-demo/perfect-dev.json --out .context/wgp-demo/perfect-freeze.json
python3 studies/wrong-goal-proof/run.py run --bundle .context/wgp-demo/bundle --split holdout --double perfect --freeze .context/wgp-demo/perfect-freeze.json --out .context/wgp-demo/perfect-holdout.json
python3 studies/wrong-goal-proof/run.py audit --bundle .context/wgp-demo/bundle --run .context/wgp-demo/perfect-holdout.json
python3 studies/wrong-goal-proof/run.py analyze --bundle .context/wgp-demo/bundle --run .context/wgp-demo/perfect-holdout.json --out .context/wgp-demo/perfect-analysis.json
```

Repeat the development/freeze/holdout commands using `--double local-only` and
new `local-*` output paths to exercise false-guarantee detection. This double
deliberately trusts the candidate verdict in **all three** presentations. It does
not simulate a model or encode an advantage for S. The `perfect` double parses
the visible controlled task and solves the original exactly. `abstain` and
`malformed` exercise failure accounting and should fail the pilot stop rule.

Each run also writes an append-only `*.json.events.jsonl` journal, flushed after
each call and outcome. An interrupted journal is diagnostic evidence, not a
completed evaluation. There is no automatic resume, retry, or background work.

Export/check every false guarantee independently:

```sh
python3 studies/wrong-goal-proof/run.py export-evidence --bundle .context/wgp-demo/bundle --run .context/wgp-demo/local-holdout.json --out .context/wgp-demo/counterexamples.json
python3 studies/wrong-goal-proof/run.py verify-evidence --evidence .context/wgp-demo/counterexamples.json
```

The packet includes each original contract, candidate, valid local certificate,
SAFE answer, hashes, and an original counterexample checked by both evaluators.
Standalone verification establishes those mathematical facts, **not** the
authenticity of an externally acquired model response.

## Offline adapter contract

`TestDouble` and `TranscriptAdapter` implement `complete(request) -> Reply`.
The request contains a fresh system/user pair and a prompt hash, never the
generator's reference AST, truth label, mutation family, or oracle witness.

`--transcript file.json` replaces `--double`. The file has `metadata` and `entries`.
Metadata requires `provider`, `model`, `model_version`, `sampling`, `pricing`, and
`authorization_reference`. Each entry has `id`, `prompt_hash`, `text`, and `usage`.
Usage has `input_tokens`, `output_tokens`, `reasoning_tokens`,
`cached_input_tokens`, and `cost_usd`; unknown values are `null`, not zero.
Duplicate IDs or mismatched prompts are rejected. Missing entries stay missing.

`requests` exports the initial prompts. Natural-pipeline reviewer prompts depend
on the actual translation; never substitute an oracle translation. Missing
reviewer prompts are available in the resulting journal after replaying recorded
translations. A subsequent replay must use a new output path.

Transcript replay makes no new API calls and cannot attest when responses were
obtained. It is not automatically a prospective experiment or preregistration.
A live adapter still needs explicit service/spending authorization, pinned model
and sampling settings, pricing, provider token limits, bounded acquisition, and
review of service terms. No keys or provider daemon access are needed here.

## Separately authorized live acquisition

`run_live.py` has a separate manifest, persistent budget ledger, HTTP receipts,
live auditor, pilot gate, and empirical freeze. Offline guards are unchanged.
The fixed schedule is 52 pilot +260 main role calls, at most 15 identical technical
retries across the campaign, and at most one genuine transport-correction pilot.
All 379 possible attempts must fit the assigned USD20 allocation before dispatch.
No inference or empirical result is implied by the transport unit tests.

See [LIVE.md](LIVE.md) for configuration, exclusion inventory, commands, failure
handling, and the distinction between requested output and financial reservation.

## Files

| Files | Responsibility |
| --- | --- |
| `wgp/logic.py`, `vector.py` | Strict language, renderer, independent semantics |
| `wgp/certificates.py`, `evidence.py` | Solver, checker, oracle ceiling, standalone witnesses |
| `wgp/dataset.py`, `prompts.py` | Disjoint generated cases and fixed role/presentation text |
| `wgp/adapters.py`, `pipeline.py` | Offline interfaces, natural/replay execution, rescoring |
| `wgp/records.py`, `analysis.py`, `cli.py` | Manifests, freeze rehearsal, counts and uncertainty |
| `wgp/live*.py`, `run_live.py` | Explicit acquisition, persistent budget, strict live audit and evidence |
| `tests/` | Unit and seeded property tests; no third-party testing library |

No shared infrastructure was copied from the other study. Public plans predate
this implementation; all testbed code here was added during the hackathon work.
No license is added by this study. Repository-wide licensing remains unchanged.
