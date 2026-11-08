# Prospective live acquisition

Status, 8 November 2026: implemented and CPU-tested; **zero experimental model
calls**. Credential access and the final source/configuration-bound coordinator
preflight are unresolved. There is no real pilot, empirical freeze, holdout result,
or empirical report/PDF yet. No transport fixture qualifies as a real pilot.

## Scope and stop rules

The scientific design in [DESIGN.md](DESIGN.md) is unchanged. Natural drift and
planted faults remain separate. Every reviewer sees the original task. B/N/S
share the same candidate and complete certificate; only the heading differs.
No extra model, hidden original, or no-certificate arm is introduced.

| Stage | Cases | Scheduled role calls |
| --- | ---: | ---: |
| Pilot | 8 natural +8 planted +4 equivalent | 52 |
| Main | 40 natural +40 planted +20 equivalent | 260 |
| Optional genuine transport-correction pilot | Same pilot, preserved first run | At most 52 |

There are at most 15 extra technical attempts over the entire campaign, including
restarts and the optional second pilot: **379 total attempts and USD20 maximum**.
One logical request may have only one identical retry, only after timeout or
HTTP 429/502/503/504. Refusal, truncation, schema error, wrong answer, and zero
effect are outcomes, never retry triggers. Three consecutive failed logical
transports stop the campaign for diagnosis. Authorization, pricing, routing and
integrity errors stop immediately. Unknown charges are not recorded as zero.

The first two clean natural tasks double as the connection check; there is no
extra smoke batch. The pilot gate still requires at least 47/52 schema-valid
responses and 10/12 clean original cases solved in all scheduled conditions.
Fault detection or a positive S−B effect is not a gate. A null result is retained.

The correction command is deliberately narrower than general prompt tuning: it
can bind new transport implementation code after a failed real pilot, preserving
tasks, prompts, model, sampling and economic configuration. A fresh stage-specific
GO must approve the new source hash. The first pilot remains in the shared wallet.
Prompt/model changes require a separately reviewed protocol, not this command.

## Exclusions and prospective freeze

Production preparation includes the exact datasets generated from seeds 6006,
6007 and 6100–6109, plus the two inspected transport-test recipes at seed
2026110806 (one excluding seeds 6006/6007; one excluding all 12 older bundles).
The inventory contains each source dataset hash, seed, C/Q truth-vector pairs,
and atom-erased original AST skeletons. Its own hash is recorded in the manifest.
Additional inspected bundles must be passed with `--exclude-dataset` before use.
The production acquisition driver checks that all 14 known sources are present.

Both new splits exclude those pairs and skeletons; main also excludes the new
pilot's original/candidate pairs and original skeletons. Equivalent variants of
one case remain intentionally paired. Common primitives and mutation templates
are not excluded, and no new-family or unrestricted mathematical generalization
is claimed. Bounded proposal exhaustion stops generation instead of relaxing the
filter. Unit tests use fixed recipes, not the eventual empirical seed.

The pilot gate additionally checks the union of C/Q functions of the **actual**
translator outputs from **all preserved pilots**, including a failed first pilot,
against every future main original/candidate. A collision stops freeze and cannot
justify an interface-repair repeat;
the implementation does not automatically resample a more convenient main set
after model answers have been observed.

The manifest freezes source and test file hashes, Python version, exact prompts,
model/provider/settings, dataset, exclusions, role/condition order and budget
caps before acquisition. The GO binds the manifest, configuration, source hashes
and permitted stages. Main additionally rereads and audits the actual pilot,
recomputes its gate and run hash, and checks the unchanged shared-wallet prefix.
Changing the code after preparation invalidates acquisition until reviewed again.
Local timestamps and hashes are not a public preregistration or signed attestation.

## HTTP contract and financial bound

Only the official OpenRouter chat-completions endpoint is supported, with
`openai/gpt-oss-120b`, an explicit Together-only route, no fallback, and
`require_parameters=true`. Redirects are forbidden. There are no provider-daemon
calls, hidden SDK retries, tools, web plugins, alternate keys or account fallbacks.
The only credential lookup is `OPENROUTER_API_KEY` in the explicitly authorized
`acquire` command. No credential is read by prepare, preflight, audit or import.

The exact JSON configuration has these required fields; there is no approved
tariff/default configuration shipped as if it had already been verified:

| Fields | Meaning |
| --- | --- |
| `version`, `model`, `provider_slug`, `provider_response_name` | Version 1; fixed model/route and required response identity |
| `temperature`, `top_p`, `reasoning_effort`, `max_tokens` | Explicit sampling and requested completion cap |
| `context_token_bound`, `output_reservation_tokens` | Verified provider context and separately agreed billable-output ceiling |
| `max_request_bytes`, `timeout_seconds` | Request-size and at-most-60-second per-HTTP timeout |
| `input_usd_per_million`, `output_usd_per_million`, `request_usd` | Decimal price ceilings; no guessed free requests |
| `price_source`, `price_as_of`, `quota_usd` | Dated official tariff source; study quota exactly 20 |
| `data_collection`, `version_pin_status` | Explicit allow/deny policy; disclose any mutable model-alias limitation |

For each physical attempt, the wallet reserves

`(context_token_bound * input_price + output_reservation_tokens * output_price) / 1_000_000 + request_price`.

This uses the full confirmed input context, not an estimated local tokenizer
ratio. The maximum over all 379 attempts must fit USD20. The completion reservation
may exceed requested `max_tokens` to cover an explicitly agreed provider accounting
margin; the request cap is not silently raised. Usage above the requested cap is
reported separately; usage above the reserved cap is fatal. Response identity,
completion/total/reasoning/cache usage and billed cost are checked again by audit.
Exact supported routing fields, final tariffs and output margin still require
the common preflight; passing parser tests is not provider confirmation.

The exclusive campaign lock spans reservation, dispatch and settlement. Every
reservation is hash-chained, appended and fsynced before HTTP. An abandoned or
unknown-charge reservation remains fully committed after restart. Known provider
cost is retained, including a pricing overrun; a recorded overrun prevents further
requests. The ledger enforces per-stage logical caps and global retry/attempt caps.
There is no implicit resume, new wallet per stage or automatic budget release.

## Reproducible commands

Run from the repository root. Choose a private, non-versioned campaign directory.
The example paths below are placeholders for approved configuration/GO files;
do not put credentials in either file. Set `WGP_FRESH_SEED` to the prospectively
chosen uint32 seed, not an engineering seed. An approved secret attachment is
provided by the execution environment only when running acquisition.

```sh
python3 studies/wrong-goal-proof/run_live.py --help
python3 studies/wrong-goal-proof/run_live.py prepare --campaign .context/wgp-live/campaign --configuration .context/wgp-live/configuration.json --seed "$WGP_FRESH_SEED"
python3 studies/wrong-goal-proof/run_live.py preflight --campaign .context/wgp-live/campaign --go .context/wgp-live/go.json --stage pilot-v1
python3 studies/wrong-goal-proof/run_live.py acquire --campaign .context/wgp-live/campaign --go .context/wgp-live/go.json --stage pilot-v1
python3 studies/wrong-goal-proof/run_live.py pilot-gate --campaign .context/wgp-live/campaign --stage pilot-v1
python3 studies/wrong-goal-proof/run_live.py freeze --campaign .context/wgp-live/campaign
python3 studies/wrong-goal-proof/run_live.py acquire --campaign .context/wgp-live/campaign --go .context/wgp-live/go.json --stage main
python3 studies/wrong-goal-proof/run_live.py audit-campaign --campaign .context/wgp-live/campaign
python3 studies/wrong-goal-proof/run_live.py analyze --campaign .context/wgp-live/campaign --stage main --out .context/wgp-live/main-analysis.json
python3 studies/wrong-goal-proof/run_live.py export-evidence --campaign .context/wgp-live/campaign --stage main --out .context/wgp-live/counterexamples.json
python3 studies/wrong-goal-proof/run_live.py verify-evidence --evidence .context/wgp-live/counterexamples.json
```

The GO schema is `version`, `decision`, `study`, `configuration_hash`,
`code_hashes_hash`, `manifest_hash`, `allowed_stages`, `approved_at`,
`authorization_reference`, and `quota_usd`. It is an explicit coordinator record,
not something acquisition creates or self-approves. A source hash is not a
cryptographic identity check on the author of that record.

`preflight` is a CPU-only source/manifest/GO check, not a balance, credential or
provider capability test. Acquisition repeats all checks and also enforces the
full inspected-source inventory, pilot/freeze relationship and persistent wallet.
No API call is needed merely to prepare, review or audit this implementation.

## Records, evidence and failure handling

Each stage preserves a flushed/fsynced intent/receipt/call/outcome journal. Visible
answers, request IDs, HTTP status, locally measured latency, token usage and cost
are retained. Reasoning-text fields are discarded; reasoning-token counts remain.
The HTTP client redacts its credential if a provider unexpectedly echoes it.
Only selected nonsecret response headers are retained. Private raw records are
not committed; public result/evidence files require a separate sanitization review.

Completed stage audit reconstructs every request, recomputes retry eligibility,
binds reservations and settlements to each physical receipt, rejects duplicate
provider IDs, reparses visible answers, and rechecks certificates/counterexamples.
Campaign audit checks previous-stage prefixes and current wallet equality. A torn
or incomplete stage fails closed; journals and unreleased reservations remain for
manual diagnosis. Do not delete them, start another campaign, or silently rerun.

Live false-guarantee packets contain the actual visible answer and acquisition
ID, exact original/candidate/certificate, and a counterexample verified by both
evaluators. Request payloads are reconstructed from those mathematical objects.
The standalone verifier establishes mathematical and record consistency, **not**
cryptographic provider origin. Empty packets are valid when no false guarantee
was observed, but the full analysis must still report utility and missingness.

Analysis preserves paired contract-level contrasts, uncertainty, abstentions and
all scheduled denominators. Cost/token accounting sums every physical attempt,
including failed/retried attempts; unknown totals stay null. The first false
guarantee in the frozen order is the primary example, if one exists. A zero count
must be reported with its upper bound and narrow scope, not as model safety.

Official interface references read during preparation:
[API overview](https://openrouter.ai/docs/api/reference/overview),
[provider selection](https://openrouter.ai/docs/guides/routing/provider-selection).
These document interface fields, not this study's as-yet-unapproved live tariff.