<!-- METHODS.md is generated from METHODS.template.md by `python build.py`. Edit the template, not METHODS.md. -->
# Methods: coverage and break-even

> **Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire.**

Data as of 2026-11-16 (block 224,788,996; DefiLlama through 2026-11-15); NEAR price $3.19 (spot at collection).

## Definitions

**Security budget (cost).** Annual issuance in NEAR × NEAR price.
- *Today's cost* uses **net** issuance: the change in `total_supply` between the head block and the block 31 days earlier, annualised by the real seconds between them. That is 2.487%/yr, or $104M/yr at $3.19. Because `total_supply` already falls when transaction fees are burned, this number is net of burn.
- *Target cost* is the 1.6% issuance approved in Nov 2026: 1.6% × total supply × price = $67M/yr. Break-even and coverage-after-the-cut use this.

**Revenue.** DefiLlama `dailyRevenue` for `near-intents` (NEAR's captured share of Intents fees), summed per day.
- *Run-rate* = trailing **90-day** average × 365 = $21.5M/yr (90-day average $59k/day).

**Coverage** = run-rate ÷ today's cost = 21%. The T3 tripwire's bear trigger instead reads a month-end series (trailing 90-day revenue at each month-end ÷ that month's issuance cost at that month's average price); its latest value is 12% for Oct 2026.

**Capture rate** = revenue ÷ volume over the same window: 4.23 bps over 90 days, 4.35 bps over 30 days ($1.7M of revenue on $3.91B of volume).

**Break-even volume/day** = target cost ÷ 365 ÷ capture rate = **$433M/day** (×3.1 today's $139M).

## Gross vs net issuance

The "trailing 30-day net-of-burn issuance" definition used elsewhere is the same quantity as ours, measured over 31 days instead of 30. The other common choice is **gross** issuance, the NEAR minted at each epoch boundary before burn. Measured on the last completed epoch (blocks 224740337, 224783536, 224783537): gross 2.496%/yr vs net 2.478%/yr; burn offset 0.72% of the mint. So choosing gross over net changes the cost, and break-even, by about that share and no more.

## Break-even under other inputs

All rows use the snapshot price above. Only the named input changes.

| Variant | Annual cost (USD) | Capture (bps) | Break-even volume/day | vs ours |
|---|---|---|---|---|
| ours: 1.6% target issuance, trailing 90-day capture | $67M | 4.23 | $433M | x1.00 |
| 30-day revenue window (capture = 30-day revenue / 30-day volume) | $67M | 4.35 | $422M | x0.97 |
| today's net issuance (31 d) instead of the 1.6% target | $104M | 4.23 | $674M | x1.55 |
| today's net issuance + 30-day revenue window | $104M | 4.35 | $656M | x1.51 |
| today's gross issuance (epoch mint, before burn) | $104M | 4.23 | $676M | x1.56 |
| today's gross issuance + 30-day revenue window | $104M | 4.35 | $658M | x1.52 |

Other entries have reported break-even volumes of about $755M–$804M a day (figures reported by those entries, not verified here). No variant here lands inside that range. Of the single-input changes, the one that moves break-even most is today's net issuance (31 d) instead of the 1.6% target (x1.55, $674M/day); the 30-day revenue window moves it x0.97, and gross instead of net issuance adds only x1.004. The remaining gap is not explained by these inputs; it would need the other entries' own price, window or cost definition, which this repo does not have.

## What is not modelled

Price is a single spot value; a different price moves cost and break-even proportionally. Revenue is DefiLlama's definition, which it revises for recent days (see `data/raw/<date>/defillama.json` and WEAKNESSES.md).
