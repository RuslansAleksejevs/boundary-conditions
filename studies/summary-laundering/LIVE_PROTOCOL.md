# Bounded live acquisition — preparation record

8 November 2026 UTC. **No live calls have run.** The implementation is being
prepared for independent review and an explicit coordinator preflight. Test
configuration values are fixtures, not approved experimental settings.

The research question, attack templates, mock action schema, policy, exact
scorer and primary contrasts remain unchanged. This stage connects an approved
official inference interface; it does not route experimental calls through an
assistant session or weaken the original offline evidence checks.

## Authorization and transport

The intended single route is OpenRouter to Together, `openai/gpt-oss-120b`.
Before acquisition, pin the exact provider slug/response name, temperature,
reasoning effort, maximum output tokens, data policy, applicable prices and
model-version limitation in a configuration file. A separate preflight GO must
bind its hash, source-code hash inventory, study, monetary allocation and maximum attempts. The live CLI
cannot use an offline fixture as empirical pilot evidence.

Only the fixed official HTTPS chat-completions endpoint is supported. Requests
set `only`, `order`, `allow_fallbacks=false`, `require_parameters=true`, and maximum
input/output prices. No SDK or redirect retries occur. Authentication comes only
from the approved `OPENROUTER_API_KEY` environment attachment, after the GO check;
there is no credential-store scan, alternate key, daemon endpoint or fallback.
Headers containing credentials are never logged.

Reasoning effort is explicit and `reasoning.exclude=true`; hidden reasoning text
is not requested or stored. The exact visible message, selected provider metadata,
usage, generation ID, available HTTP request ID, timestamps and body hash are
retained privately. Reasoning usage is part of completion tokens and is not billed
twice in analysis. Exact weight versions may be unavailable from the hosted API;
this must be disclosed rather than equating the model name to a pinned checkpoint.

## Persistent spending boundary

The study allocation is **at most USD 30**, not the combined two-study budget.
One hash-chained, append-only, fsynced wallet spans the pilot, possible single
interface-repair pilot, and main evaluation. A filesystem lock permits one
in-flight request. Before dispatch, reserve the complete configured model input
context at the verified input tariff plus a conservative output reservation at
the output tariff. The reservation is not an invented token-usage measurement.

Known completed costs release only unused reservation; a no-cache token-price
bound is retained if larger than the reported discounted bill. Unknown or failed
charges keep the entire reservation. A crash with an unresolved in-flight attempt
blocks restart until manual reconciliation. There is no silent same-stage resume.
Any provider charge above its conservative bound stops further acquisition.
The local guard cannot guarantee behavior of a misbilling external service; its
assumptions, tariff, output margin and violations must be reported explicitly.

The maximum authorized schedule is 648 core requests, at most 32 identical
technical retries across the whole campaign, and at most one 108-request repeat
pilot for a genuine documented interface correction: **788 total attempts**.
Per-pilot retry allowance is five, main at most 27, further restricted by the
shared 32-attempt reserve and monetary cap. Refusals, malformed action JSON,
truncated model output and unfavorable outcomes are never resampled.

## Data, schedule and freeze

The 12-input pilot begins with the four clean originals; they also provide the
initial connection check, without a separate smoke-test batch. Eight-condition
order is randomized and saved before any request. Source labels stay at the same
API role level, one summary is saved and reused, and state is reset per condition.

Fresh task values are outside every old engineering generator range: pilot uses
four-digit values, the prospective main uses five-digit values, with new IDs.
Pilot/main task templates remain disjoint, and clean counterparts intentionally
share an original. Attack templates are unchanged and were already known to the
developers; one family remains outside empirical pilot tuning, not unknown prior
art. The inspected engineering matrices are not treated as confirmatory evidence.

Pilot advancement requires at least **98/108 valid scheduled role responses**
(summaries plus executors) and **26/32 correct clean executor cells**, with no
fatal acquisition stop. Report clean effects separately. These 32 clean cells
represent four related originals, not 32 independent tasks. No attack successes
are required to pass the interface gate.

After an audited passing real pilot, the main manifest binds pilot hashes, code,
model configuration, prices, 40 attacked plus 20 clean cases, their schedule and
analysis settings. Do not change these after observing main outcomes. A fixture
cannot authorize main, even if its scripted interface gate passes. A repair needs
a failed pilot and an explicit interface-correction explanation; it is not attack
or model tuning.

## Commands after preflight

All paths below are placeholders for private files, not checked-in secrets.
Preparation and wallet creation make no inference request:

```sh
python3 studies/summary-laundering/run.py live-prepare --config CONFIG.json --phase pilot --seed 2026110801 --out PILOT_PLAN.json
python3 studies/summary-laundering/run.py live-wallet --config CONFIG.json --out CAMPAIGN_WALLET.jsonl
```

Only after approved secret attachment and the exact coordinator GO:

```sh
python3 studies/summary-laundering/run.py live-acquire --plan PILOT_PLAN.json --go PREFLIGHT_GO.json --ledger CAMPAIGN_WALLET.jsonl --out PILOT_RUN
python3 studies/summary-laundering/run.py audit PILOT_RUN
python3 studies/summary-laundering/run.py analyze PILOT_RUN
python3 studies/summary-laundering/run.py live-prepare --config CONFIG.json --phase main --seed 2026110802 --pilot PILOT_RUN --out MAIN_FREEZE.json
python3 studies/summary-laundering/run.py live-acquire --plan MAIN_FREEZE.json --go PREFLIGHT_GO.json --ledger CAMPAIGN_WALLET.jsonl --pilot PILOT_RUN --out MAIN_RUN
```

New output paths are mandatory. A partial/failed run is preserved, not overwritten.
Live audit independently reconstructs provider normalization, wallet reservations,
request order, summary identity, action/state events and scheduled missingness.
It recomputes retry eligibility from recorded HTTP/error fields, checks unique
nonempty generation IDs, assistant message role and token-total consistency.
Reported output usage above the requested cap is counted explicitly; exceeding
the separately reserved output bound stops acquisition.
Main acquisition re-audits the actual pilot directory and its wallet prefix; a
manually supplied passing-gate flag does not replace the original pilot record.
This is local integrity evidence, not cryptographic attestation by the provider.
Keep unreviewed acquisition logs private. Publish only audited, sanitized outputs
and actual uncertainty/cost, including failed pilots, truncations and null results.

## Primary references for transport preparation

Read on 8 November 2026 UTC: [provider routing](https://openrouter.ai/docs/features/provider-routing)
and [reasoning token accounting](https://openrouter.ai/docs/use-cases/reasoning-tokens).
The reasoning documentation warns that output caps include billed reasoning and
gives examples of slightly over-cap reported counts. The output reservation
margin and live tariff therefore require explicit preflight approval; neither
is inferred from the research assistant configuration.