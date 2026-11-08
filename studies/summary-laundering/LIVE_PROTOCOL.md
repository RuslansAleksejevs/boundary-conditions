# Bounded live acquisition

8 November 2026 UTC. Two real development stages made 60 API attempts and stopped;
no main freeze or held-out acquisition has run. See [current state](STATE.md) and
the explicit [operational amendment](OPERATIONAL_AMENDMENT.md). Test configuration
values remain fixtures, not authorization for an experimental batch.

The research question, attack templates, mock action schema, policy, exact
scorer and primary contrasts remain unchanged. This stage connects an approved
official inference interface; it does not route experimental calls through an
assistant session or weaken the original offline evidence checks.

## Authorization and transport

The user-selected single route is OpenRouter to Alibaba,
`qwen/qwen3.5-122b-a10b`. The earlier Together/gpt-oss configuration was a
preparation fixture, never a model evaluation or outcome-based model choice.
Before acquisition, pin the exact provider slug/response name, temperature,
top-p, reasoning enablement, maximum output tokens, data policy, applicable prices and
model-version limitation in a configuration file. A separate preflight GO must
bind its hash, source-code hash inventory, study, monetary allocation and maximum attempts. The live CLI
cannot use an offline fixture as empirical pilot evidence.

Only the fixed official HTTPS chat-completions endpoint is supported. Requests
set `only`, `order`, `allow_fallbacks=false`, `require_parameters=true`, and maximum
input/output prices. They use SSE (`stream=true`) with final usage requested.
No SDK or redirect retries occur. Authentication comes only
from the approved `OPENROUTER_API_KEY` environment attachment, after the GO check;
there is no credential-store scan, alternate key, daemon endpoint or fallback.
Headers containing credentials are never logged.

Reasoning uses explicit `reasoning.enabled` and `reasoning.exclude=true`; the
selected endpoint does not advertise `reasoning_effort`, so it is not sent. Hidden reasoning text
is not requested or stored. The exact visible message, selected provider metadata,
usage, generation ID, available HTTP request ID, timestamps and body hash are
retained privately. Sanitized SSE events are retained; raw stream bytes are hashed
through the terminal marker but not persisted. A complete answer requires a
terminal finish, complete final usage, consistent identity and `[DONE]`. Partial
or timed-out streams never become complete outcomes. Reads are bounded by eight
million bytes and 180 seconds total wall time. The operational amendment adds a
POSIX total timer to the shrinking socket timeout, covering a slowly dripped line.
Reasoning usage is part of completion tokens and is not billed
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

The verified Alibaba quote is USD 0.26/2.08 per million input/output tokens,
with a 262,144-token native context. Reserve that full context separately for
input and billed output: **USD 0.61341696 per attempt**. The explicit assumption
is that the advertised native context bounds the entire sequence, including
reasoning. The endpoint's 65,536 completion listing is not assumed to include
all hidden reasoning. Reported violations halt acquisition.
Multiplying the conservative bound by all 788 authorized attempts gives
USD 483.37256448, **not** a spending authorization or expected expense.
The USD 30 wallet remains binding before every dispatch; confirmed settlements
release only unused reserve. This guards expenditure but does not guarantee that
all planned calls fit under worst-case token use. Pilot cost/time must be reviewed
before main freeze; any budget stop preserves the remaining scheduled missing rows.

The fixed requested `max_tokens` is 8,192, temperature 0.6 and top-p 0.95.
Native Alibaba documentation describes this token parameter as an answer cap
excluding reasoning for these models; it is therefore not used as the billed
output bound. No response-format override or reasoning-budget guess is added.
The model's native thinking endpoint is documented as streaming-only, motivating
the SSE adaptation before any observations.

Routing uses `data_collection="allow"`: provider metadata reports prompt logging
with 30-day retention, no training on submitted data, and no zero-retention
guarantee. Only synthetic study tasks are sent, never private coordination or
personal context. This policy is explicit rather than claiming incompatible ZDR.

The maximum authorized schedule is 648 core requests, at most 32 identical
technical retries across the whole campaign, and at most one 108-request repeat
pilot for a genuine documented interface correction: **788 total attempts**.
Per-pilot retry allowance is five, main at most 27, further restricted by the
shared 32-attempt reserve and monetary cap. Refusals, malformed action JSON,
truncated model output and unfavorable outcomes are never resampled.
After three consecutive failed logical transport calls, acquisition stops and
the remaining scheduled cells stay missing. The counter resets after a successful
transport; model refusals, invalid answers and truncation do not trip this outage
circuit. The circuit never selects an alternative provider.

The stopped repair pilot has a separately authorized **implementation**, not
execution, of one operational continuation. It can acquire only the exact 54
never-attempted suffix roles, with zero new retries and at most 113 total attempts
including the original 59. It preserves the original failed run/gate and all
financial holds. See the amendment for the pre-data disclosure and full limits.
Attempt starts are spaced at least 20 seconds, including a conservative initial
pause in a new process. The provider route must be exclusive to one study.
After HTTP 429, a minimum 60-second cooldown honors a longer normalized
Retry-After up to 300 seconds; a larger delay stops without another attempt.
Wait chunks are at most 30 seconds. This applies to the next logical request as
well as an already-authorized main retry; it grants no additional retry.

## Data, schedule and freeze

The 12-input pilot begins with the four clean originals; they also provide the
initial connection check, without a separate smoke-test batch. Eight-condition
order is randomized and saved before any request. Source labels stay at the same
API role level, one summary is saved and reused, and state is reset per condition.

Fresh task values are outside every old engineering generator range: pilot uses
four-digit values, the prospective main uses five-digit values, with new IDs.
The inspected live-interface fixtures are also excluded explicitly by their
IDs, facts and raw text; their old illustrative pilot seed is not reused.
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
python3 studies/summary-laundering/run.py live-prepare --config CONFIG.json --phase pilot --seed 2026110811 --out PILOT_PLAN.json
python3 studies/summary-laundering/run.py live-wallet --config CONFIG.json --out CAMPAIGN_WALLET.jsonl
```

Only after approved secret attachment and the exact coordinator GO:

```sh
python3 studies/summary-laundering/run.py live-acquire --plan PILOT_PLAN.json --go PREFLIGHT_GO.json --ledger CAMPAIGN_WALLET.jsonl --out PILOT_RUN
python3 studies/summary-laundering/run.py audit PILOT_RUN
python3 studies/summary-laundering/run.py analyze PILOT_RUN
python3 studies/summary-laundering/run.py live-prepare --config CONFIG.json --phase main --seed 2026110812 --pilot PILOT_RUN --out MAIN_FREEZE.json
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

## Explicit operational continuation

These commands do not silently resume the ordinary acquisition stage. Preparation
checks the exact interrupted parent and creates a new immutable amendment plan:

```sh
python3 studies/summary-laundering/run.py continuation-prepare --parent REPAIR_RUN --out CONTINUATION_PLAN.json
```

After independent review, a new GO must additionally bind `continuation_plan_hash`
and `provider_route_exclusive=true`. It still binds the configuration, amended
source inventory, study budget and campaign cap. No inference occurs without it:

```sh
python3 studies/summary-laundering/run.py continuation-acquire --parent REPAIR_RUN --plan CONTINUATION_PLAN.json --go CONTINUATION_GO.json --ledger CAMPAIGN_WALLET.jsonl --out CONTINUATION_RUN
python3 studies/summary-laundering/run.py audit CONTINUATION_RUN
python3 studies/summary-laundering/run.py analyze CONTINUATION_RUN
```

The new directory contains the original manifest unchanged, the distinct
continuation plan, new-call event records and a clearly labeled composite run
embedding its immutable parent. The original 59 calls are locally replayed for
state reconstruction, never sent again. The union audit requires unchanged prior
calls, outcomes, summaries and ledger prefix, disjoint new first attempts,
preserved scientific modules/function hashes, exact pacing and the original
combined cap. The original failed gate remains available alongside the amended
composite gate. The analysis functions and thresholds are unchanged.

A future main freeze must bind the audited composite's actual run and amendment
hashes and its effective acquisition-source inventory. A standalone passing flag,
an old failed pilot, or a fixture cannot qualify it. Main has a separately frozen
20-second minimum start spacing and still requires a new explicit GO.
Its manifest also binds the same 60/300-second HTTP 429 cooldown/stop policy.

## Primary references for transport preparation

Read on 8 November 2026 UTC: [provider routing](https://openrouter.ai/docs/features/provider-routing)
and [reasoning token accounting](https://openrouter.ai/docs/use-cases/reasoning-tokens).
The reasoning documentation warns that output caps include billed reasoning and
gives examples of slightly over-cap reported counts. The output reservation
margin and live tariff therefore require explicit preflight approval; neither
is inferred from the research assistant configuration.

The [selected endpoint listing](https://openrouter.ai/api/v1/models/qwen/qwen3.5-122b-a10b/endpoints)
was reread before acquisition: tag `alibaba`, response provider `Alibaba`, display
name dated `20260224`, context 262,144, maximum completion 65,536. A dated display
name is not proof of an immutable served weight revision. The
[official model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B)
documents thinking mode and sampling recommendations; hosted support is checked
against the endpoint, not assumed from self-hosted examples.
Native API caveats were verified in Alibaba's
[deep-thinking documentation](https://www.alibabacloud.com/help/en/model-studio/deep-thinking)
and [Chat Completions reference](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-openai-chat-completions).