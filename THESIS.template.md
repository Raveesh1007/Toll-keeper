<!-- THESIS.md is generated from THESIS.template.md by `python build.py`. Edit the template, not THESIS.md. -->
# NEAR: a toll on cross-chain settlement, if the toll can pay for the road

**Draft 3 · data as of {asof} (block {height}; DefiLlama through {llama_end}) · NEAR ${price}**

Every number tagged M or D below is computed by `python build.py` from the raw files in `data/raw/`, which `python collect.py` fetches. Nothing is typed in by hand. Tripwires and the verdict rule were pre-registered in commit `{reg_commit}` (`config/tripwires.json`, {reg_note} registration).

## The long-term case in one paragraph

NEAR is turning into a paid settlement layer for value that moves between chains. Users already pay about **{fees_annual} a year** in fees to move value through NEAR Intents. That is {fees_vs_target} of what it would cost to secure NEAR once issuance falls to 1.6%. Three things are moving in the holder's favour at once: the **cost of security is falling by design**, NEAR is **keeping a growing share of each swap**, and the **trust layer those swaps depend on is hardening**. NEAR is a long-term hold if its captured revenue compounds at **about {required_cagr} a year** until the issuance cut is fully in place ({full_cut}) without a failure in the signing layer. From {hg_from} (the first full month after the fee switch) to {hg_to}, monthly revenue grew x{hg_ratio}, but about {cap_share} of that came from a higher capture rate, and volume is not compounding yet: {mtd_range} averaged {mtd_now} a day, {vol_yoy_mtd} on the same days of 2025. (The 90-day year-on-year figure, {vol_yoy_90}, compares against Intents' 2025 ramp-up, so it overstates the trend.) So the case is **{verdict_lower}**.

## Verdict: {verdict}

| Test | Hurdle | Observed | Pass? |
|---|---|---|---|
| Revenue growth | >= {hurdle}/yr (pre-registered; {required_cagr}/yr is what today's numbers need) | {headline_growth} | {t1_pass} |
| Coverage of security cost | 100% | run-rate (trailing 90-day average × 365): {coverage} ({run_rate} vs {budget} issuance); month-end series (trigger input): {cov_me_last} for {cov_me_month} | {t3_pass} |
| Trust layer | No loss in the signing core; decentralizing | {m180_mpc} 180 days ago, {mpc_now} now; {mpc_losses} | {trust_pass} |

## Pillar 1: The fee pool already exists

{claims_P1}

Reading: the money to fund NEAR's security is already flowing through NEAR's product. Most of it goes to solvers and distribution partners, who are needed to keep volume, so NEAR cannot take all of it. The question is NEAR's share and the volume growth, not whether demand exists.

## Pillar 2: Value captured is rising fast

Every month DefiLlama has, from its daily series (`data/raw/<date>/defillama.json`; the provided seed files in `data/defillama/` are checked to match exactly for every day except the latest 7, which DefiLlama revises):

{monthly_table}

**Reading the gaps in this table.** `not tracked` means DefiLlama has no figure for that month: its swap-volume series starts on {vol_start}, and its fee and revenue series start on {fees_start}. Revenue shows `$0` (or a few dollars) up to {rev_material}, and the capture rate there is `0.00`, because NEAR was not yet capturing revenue that DefiLlama counts; those zeros are reported values, not missing data. Revenue from {rev_material} up to the {fee_switch} fee switch (when buybacks began) is lumpy treasury sweeps rather than steady income, so read it with caution. The headline growth figure (claim P2.1) uses only months after the switch. The 6-month comparison in claim P2.4 starts {prior_start}, which includes a few pre-switch days, so it is kept as a detail only.

{claims_P2}

## Pillar 3: The cost of security is falling by design

Net issuance and its dollar cost, month by month, from `total_supply` at archival blocks on the first of each month (cost = NEAR issued x average daily price that month, price from `coins.llama.fi`):

{budget_table}

{claims_P3}

## Pillar 4: The trust layer is hardening (the precondition)

Intents moves real assets across 35+ chains through the Chain Signatures MPC network. If that network fails, the toll road closes. This is why security is the precondition of the bull case, not a side topic.

`v1.signer` state at the first block of each month (FastNEAR archival) and at head:

{mpc_table}

{claims_P4}

## The bear case (kept in full)

- **Volume is cyclical, not compounding yet.** {mtd_range} volume averaged {mtd_now} a day, against {mtd_prev} a day in the same days a year earlier: **{vol_yoy_mtd} year on year**. The 90-day year-on-year figure ({vol_yoy_90}) compares against Intents' 2025 ramp-up (see the monthly table). The six-month surge partly recovers a dip, not a new trend. Last 30 days vs the 30 before: volume {d30_vol}, fees {d30_fees}, revenue {d30_rev}.
- **Capture rate has a ceiling.** About {cap_share} of the x{hg_ratio} rise from {hg_from} to {hg_to} came from NEAR taking more per swap. Gross fees are {fee_bps} bps; NEAR already keeps {share30}. Squeezing distribution partners harder risks losing volume to them. From here growth must mostly come from volume.
- **Price works against holders.** Buybacks are paid in dollars, so a higher NEAR price buys fewer NEAR, and the issuance bill in dollars rises. A rally widens the gap unless revenue outruns it.
- **Bought-back NEAR is held, not burned.** The buyback wallet went from {bb_180} NEAR 180 days ago to {bb_now} now, while supply kept growing {iss31_pct} a year. Holders are still diluted today.
- **Lower issuance thins the security budget.** Gross staking yield falls from ~{yield_now} to ~{yield_target} at 1.6%. If stakers leave, the base chain weakens exactly when the toll road needs it.
- **Concentrated trust.** {threshold} of {participants} operators can sign on all {domains} key domains and redeploy the signing contract with no delay window. Participants went from {p30} to {participants} in the last 30 days.
- **Two incidents in NEAR-run products in 2026**, neither in the signing layer (incident ledger: `data/incidents.json`). In the second, the agents reached ran on an older deployment that, per the cited article, "did not run inside the company's TEE".

## What has to be true by {full_cut}

At today's capture rate of {capture} bps, revenue of {budget_target}/yr needs about **{be_vol} of Intents volume a day, {be_mult}x today's {t90_vol}**. Equivalent paths: volume x{vol_x_6} with capture at 6 bps, or volume x{be_mult} with capture flat. Anything that holds that path for {months_left} months while the signing layer stays clean makes NEAR a long-term hold on these terms.

## Tripwires (pre-registered in `{reg_short}`)

{tripwire_table}

**Verdict rule.** HOLD when T1 and T3 bull triggers both fire with no bear trigger. VOID if T6 fires. DON'T HOLD if two bear triggers fire. Otherwise ON TRACK, UNPROVEN.

**Dated predictions:**

{prediction_table}

## Optional upside, not counted

NEAR AI (confidential inference used by Brave Leo, 1M+ NEAR staked to pay for inference) is real usage, but none of its revenue is shown reaching the buyback wallet, and stake-for-inference spends staking rewards rather than adding revenue. It is excluded from the case until that changes.

## What this thesis cannot prove

Price targets; total value secured by MPC keys (DefiLlama's {tvl} Intents TVL is only a floor); whether high audit findings are fixed in deployed {mpc_version}; whether the deployed code hash matches a tagged `near/mpc` release; validity of TEE quotes; whether solvers would accept a higher NEAR take rate. The buyback wallet balance is a lower bound on purchases (transfers out are not traced). Stake history starts at this repo's first snapshot, because `validators` at past blocks is not served by archival nodes. Incidents (T6, T7) are entered by hand in `data/incidents.json` with sources.

**T1 validity rule. Added 2026-11-14, after pre-registration.** A T1 comparison (trailing 90 days vs the 90 days ending 180 days earlier) counts only if that earlier window starts on or after {t1_valid_from_rule} (the pre-registered `clean_data_start`); otherwise it is `n/a` with the reason "{t1_rule}", because NEAR's revenue before the fee switch was near zero and inflates any ratio built on it. The threshold and state logic are unchanged. Under this rule the first valid comparison is {t1_valid_from}, valid quarter-ends so far: {t1_valid_n}, qualifying: {t1_qualifying}; the next quarter-end evaluated is {t1_next_q}. The same reasoning moved the headline growth figure to post-switch months (claim P2.1).

**T2 base effect.** The 90-day year-on-year volume figure ({vol_yoy_90}) compares against Intents' 2025 ramp-up; month-to-date year on year is {vol_yoy_mtd}. T2's threshold and state logic are unchanged.

How coverage and break-even are computed, and how break-even moves under other inputs: [METHODS.md](METHODS.md).

## Status key and sourcing

**M** = measured on NEAR mainnet or FastNEAR archival RPC · **D** = DefiLlama public API · **S** = primary source or established outlet · arith = computed here from M/D values. No other hackathon entry is cited as evidence.
