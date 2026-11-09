# Main operational audit

As of 9 November 2026. PROJECT_REPORTED from immutable local acquisition records;
not a signed provider attestation. All checks are CPU-only and made zero new API
requests. The acquisition process actually exited with code 0.

| Item | Verified value |
| --- | --- |
| Scheduled roles / physical attempts | 540 / 548 |
| HTTP 200 / HTTP 429 | 538 / 10 |
| Valid summaries | 60 |
| Valid / invalid / missing executor cells | 445 / 33 / 2 |
| Parse failures | 32 invalid JSON; 1 invalid action schema |
| Technical retries | 8: 6 recovered, 2 exhausted |
| First request start UTC | 2026-11-08T23:53:27.348046Z |
| Last request finish UTC | 2026-11-09T03:04:13.578361Z |
| Wall duration | 11446.230315 seconds |
| Summed request latency | 3913.528154 seconds |
| Median request latency | 5.803906 seconds |
| Minimum monotonic start spacing | 20.000060 seconds |
| Minimum HTTP-429 cooldown | 60.001016 seconds |
| Campaign wallet records / settled attempts | 1329 / 662 |
| In-flight reservations | 0 |
| Original pilot wallet prefix | 232 records unchanged |
| Accepted main receipt cost | USD 1.12611330 |
| Main unknown-cost receipts | 10, all fully reserved |
| Campaign charged/reserved | USD 13.00633282 |
| Acquisition stop reason | none |

Every technical retry had identical logical-role, request and wire identities.
After the two exhausted retries the next different role began only after the
required cooldown. All ten failures remain in the ledger and public call list.
There was no semantic retry or post-hoc replacement. Missing outcomes are:

- `live-main-2026110812-009-attack/S-P` (colleague family);
- `live-main-2026110812-028-clean/R-P` (prerequisite clean counterpart).

The append-only journal's calls and summaries exactly equal the final run arrays;
its outcome records equal the outcome array after removing only the journal's
`record_type` field. The external campaign wallet exactly equals the final run's
ledger. The pilot binding, source inventory, frozen manifest, seeded schedule,
request/summary identities, event/state replay, pacing, reserve settlement and
all missingness classifications passed native verification.

| Hash | SHA-256 / canonical digest |
| --- | --- |
| Frozen main manifest | `6553e7c06a6c160f0af883c9ca24eb61361a23101745e2636f344527360aefdf` |
| Source inventory | `dbb21522554b9c96bed164d89230f6ecbb36b7d51b2861048f275a6461c424ca` |
| Final private run | `a5401cd600308f8dc10d632c0044c0bb1fc569bd3269324e68f64006d9d27c61` |
| Bound composite pilot run | `42ded5120449f41dd98b3cb4dc7bae1bb45b06dd1512fe6e67409183c5443940` |

The public replay check reproduced 60 inputs, 480 cells, 548 visible calls and two
primary contrasts. The full suite passed 166 tests in 6.235 seconds on Python
3.14.6. Locally recorded provenance is not independent replication; public data
cannot authenticate private transport receipts or account billing. No private
authorization, personal path, provider generation ID or hidden reasoning is
needed for the public replay.

Accounting addendum, 2026-11-09T03:09:27Z: a coordinator-verified official account
aggregate agreed with the receipt-derived campaign accounting. An earlier
03:04:57Z snapshot was USD 0.00117286 lower. Neither snapshot rewrites the local
unknown receipts or permits release of their full holds; no provider-internal
cause is asserted. Account payloads and identifiers remain private.