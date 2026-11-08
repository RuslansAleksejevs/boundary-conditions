# Live execution: model, funding, and limits

Snapshot: **8 November 2026, 19:48 UTC**, before experimental inference.
This records authorization and a prospective protocol, not experimental results.

## Funding

The project contributor prepaid **USD 50 in OpenRouter credits** and authorized
up to that amount for the two studies. A read-only account check confirmed
USD 50 remaining, USD 0 usage, and a USD 50 API-key limit at the snapshot above.
There is no sponsor or award claim. No automatic top-up, additional purchase,
or second experimental model is authorized by this plan.

| Study | Hard monetary cap | Core logical calls | Maximum attempts |
| --- | ---: | ---: | ---: |
| A: summary laundering | $30 | 108 pilot + 540 evaluation | 788 |
| B: certificate scope | $20 | 52 pilot + 260 evaluation | 379 |
| Combined | **$50** | **960** | **1,167** |

Maximum attempts include at most one genuinely necessary interface-correction
pilot (108/52 additional calls) and 32/15 identical technical retries. These are
ceilings, not targets or permission to tune attacks after seeing outcomes.
Research-assistant subscription use is separate from this experimental API budget.
Actual calls and costs will be reported from audited acquisition ledgers.

## Fixed experimental target

Both studies use **Qwen3.5-122B-A10B**, model ID
`qwen/qwen3.5-122b-a10b`, through **OpenRouter → Alibaba**. OpenAI and Anthropic
models are not experimental subjects in this run. This choice gives both studies
one common, externally served open-weight model; it does not establish superiority
over alternatives or equivalence to a local deployment.

| Setting | Prospective value |
| --- | --- |
| Provider slug / returned provider | `alibaba` / `Alibaba` |
| Routing | Fixed provider only; fallbacks disabled; parameters required |
| Temperature / top-p | 0.6 / 0.95 |
| Reasoning | Enabled; reasoning text excluded from response, still billable |
| Requested maximum output | 8,192 tokens |
| Conservative output reservation | Full 262,144-token context per attempt |
| Conservative input reservation | Full 262,144-token context per attempt |
| Input / output price cap | $0.26 / $2.08 per million tokens |
| Per-request fee | $0 at the checked endpoint |
| HTTP timeout | 180 seconds; no implicit SDK retries |
| Transport | Streaming SSE, with complete visible response and usage checks |
| JSON response mode | Not requested; JSON-only task instructions retained |
| Concurrency | One in-flight request per study |

Local seeds fix generated cases and condition order, not hosted-model randomness.
The public model ID is not a cryptographic pin of provider weights. Capture
returned model/provider IDs and reject unapproved routes. Provider metadata does
not disclose quantization; do not infer a precision or claim bitwise reproducibility.

## Budget stops and prospective amendment

Before every request, reserve **$0.61341696**:
`(262144 × 0.26 + 262144 × 2.08) / 1,000,000`. This deliberately pessimistic
bound reserves the full context separately for input and output, not a guessed
character-to-token conversion. The official model card describes native context
as including input and output; the endpoint advertises the same 262,144 limit.
The assumption is that this advertised limit covers the complete sequence,
including reasoning. Stop on any reported usage or price-bound violation.
Do not interpret native `max_tokens` as a proven reasoning-inclusive cap:
Alibaba documents a separate thinking budget. The initially considered 16,384
output reserve was rejected during preflight, before any model calls.
After a confirmed response, settle conservatively against reported cost and
the no-cache usage-based price bound. Unknown charges retain their full reserve.
Do not start an attempt if its reserve would breach the study's hard cap.

**Amendment made before any model observations:** admission does not require
the full campaign's worst-case reserve to fit upfront. That condition would
exclude the planned schedule even when actual short requests are inexpensive.
The per-request hard stop is unchanged. A complete evaluation is not guaranteed:
retain the fixed schedule, mark budget-stopped cases unassessed, and report
missingness bounds. Do not silently reduce samples or transfer allocations.
Pilot format/utility gates and measured cost projections precede evaluation.

## Data handling and sources

Only synthetic task records are sent. No personal project context, real tool
access, credentials in prompts, or hidden reasoning traces are part of the data.
`data_collection: "allow"` is explicit: the checked Alibaba metadata permits
prompt logging, lists 30-day retention and no training on submitted data, and
does **not** promise zero retention. Do not describe this route as ZDR.

Sources checked 8 November 2026:

- [Model/provider endpoints](https://openrouter.ai/api/v1/models/qwen/qwen3.5-122b-a10b/endpoints)
- [Provider data policies](https://openrouter.ai/api/v1/providers)
- [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection)
- [Reasoning controls and billing](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)
- [OpenRouter terms](https://openrouter.ai/terms)
- [Official Qwen model card: total context](https://huggingface.co/Qwen/Qwen3.5-122B-A10B)
- [Alibaba thinking/streaming requirements](https://www.alibabacloud.com/help/en/model-studio/deep-thinking)
- [Alibaba answer and thinking token limits](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-openai-chat-completions)
- Account funding: contributor authorization and authenticated read-only account
  check. Account identifiers, credentials, and raw account responses are private.