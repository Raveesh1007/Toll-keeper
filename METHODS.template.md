<!-- METHODS.md is generated from METHODS.template.md by `python build.py`. Edit the template, not METHODS.md. -->
# Methods: coverage and break-even

> **Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire.**

Data as of {asof} (block {height}; DefiLlama through {llama_end}); NEAR price ${price} (spot at collection).

## Definitions

**Security budget (cost).** Annual issuance in NEAR × NEAR price.
- *Today's cost* uses **net** issuance: the change in `total_supply` between the head block and the block 31 days earlier, annualised by the real seconds between them. That is {iss31_rate}/yr, or {budget}/yr at ${price}. Because `total_supply` already falls when transaction fees are burned, this number is net of burn.
- *Target cost* is the 1.6% issuance approved in Nov 2026: 1.6% × total supply × price = {budget_target}/yr. Break-even and coverage-after-the-cut use this.

**Revenue.** DefiLlama `dailyRevenue` for `near-intents` (NEAR's captured share of Intents fees), summed per day.
- *Run-rate* = trailing **90-day** average × 365 = {run_rate}/yr (90-day average {t90_rev}/day).

**Coverage** = run-rate ÷ today's cost = {coverage}. The T3 tripwire's bear trigger instead reads a month-end series (trailing 90-day revenue at each month-end ÷ that month's issuance cost at that month's average price); its latest value is {cov_me_last} for {cov_me_month}.

**Capture rate** = revenue ÷ volume over the same window: {capture} bps over 90 days, {capture30} bps over 30 days ({rev30} of revenue on {vol30} of volume).

**Break-even volume/day** = target cost ÷ 365 ÷ capture rate = **{be_vol}/day** (×{be_mult} today's {t90_vol}).

## Gross vs net issuance

The "trailing 30-day net-of-burn issuance" definition used elsewhere is the same quantity as ours, measured over 31 days instead of 30. The other common choice is **gross** issuance, the NEAR minted at each epoch boundary before burn. Measured on the last completed epoch (blocks {epoch_blocks}): gross {gross_rate}/yr vs net {net_rate_epoch}/yr; burn offset {burn_share} of the mint. So choosing gross over net changes the cost, and break-even, by about that share and no more.

## Break-even under other inputs

All rows use the snapshot price above. Only the named input changes.

{be_table}

Other entries have reported break-even volumes of about $755M–$804M a day (figures reported by those entries, not verified here). {range_verdict}

## What is not modelled

Price is a single spot value; a different price moves cost and break-even proportionally. Revenue is DefiLlama's definition, which it revises for recent days (see `data/raw/<date>/defillama.json` and WEAKNESSES.md).
