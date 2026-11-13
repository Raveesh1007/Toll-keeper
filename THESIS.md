<!-- THESIS.md is generated from THESIS.template.md by `python build.py`. Edit the template, not THESIS.md. -->
# NEAR: a toll on cross-chain settlement, if the toll can pay for the road

**Draft 3 · data as of 2026-11-13 (block 224,372,730; DefiLlama through 2026-11-12) · NEAR $3.58**

Every number tagged M or D below is computed by `python build.py` from the raw files in `data/raw/`, which `python collect.py` fetches. Nothing is typed in by hand. Tripwires and the verdict rule were pre-registered in commit `d5491d7e3e585dade85c7a6d914587c8ed10d8f3` (`config/tripwires.json`, unchanged since registration).

## The long-term case in one paragraph

NEAR is turning into a paid settlement layer for value that moves between chains. Users already pay about **$70.7M a year** in fees to move value through NEAR Intents. That is 94% of what it would cost to secure NEAR once issuance falls to 1.6%. Three things are moving in the holder's favour at once: the **cost of security is falling by design**, NEAR is **keeping a growing share of each swap**, and the **trust layer those swaps depend on is hardening**. NEAR is a long-term hold if its captured revenue compounds at **about 77% a year** until the issuance cut is fully in place (2029-01-31) without a failure in the signing layer. Over the last six months it grew far faster than that, but 46% of that growth came from a rise in the capture rate, and volume is not compounding yet: Nov 1-12 averaged $134M a day, +3.6% on the same days of 2025. (The 90-day year-on-year figure, +212.9%, compares against Intents' 2025 ramp-up, so it overstates the trend.) So the case is **on track, unproven**.

## Verdict: ON TRACK, UNPROVEN

| Test | Hurdle | Observed | Pass? |
|---|---|---|---|
| Revenue growth | >= 75%/yr (pre-registered; 77%/yr is what today's numbers need) | x4.22 in six months (+1754%/yr annualized) | **Yes**, but see the decomposition below |
| Coverage of security cost | 100% | 18% (revenue run-rate $21.1M vs $115M issuance) | No, 3.6x gap at 1.6% issuance |
| Trust layer | No loss in the signing core; decentralizing | 5-of-8 180 days ago, 11-of-16 now; no signing-layer loss | **Yes** |

## Pillar 1: The fee pool already exists

| # | Claim | Status | Value | Reproduce |
|---|---|---|---|---|
| P1.1 | Intents volume, last 30 d | D | **$3.77B** ($32.9B over 12 months) | `api.llama.fi/summary/dexs/near-intents` |
| P1.2 | Gross fees users paid, last 30 d | D | **$5.81M** = 15.4 bps of volume = **$70.7M/yr** | `summary/fees/near-intents?dataType=dailyFees` |
| P1.3 | Gross fees vs security budget at 1.6% issuance ($75.1M/yr) | arith | **94%** | P1.2 / (1.6% x supply x price) |
| P1.4 | NEAR's captured share of fees, last 30 d | D | **31.6%** ($1.84M of $5.81M) | `dataType=dailyRevenue` |

Reading: the money to fund NEAR's security is already flowing through NEAR's product. Most of it goes to solvers and distribution partners, who are needed to keep volume, so NEAR cannot take all of it. The question is NEAR's share and the volume growth, not whether demand exists.

## Pillar 2: Value captured is rising fast

Every month DefiLlama has, from its daily series (`data/raw/<date>/defillama.json`; the provided seed files in `data/defillama/` are checked to be an exact subset):

| Month | Days | Volume | Gross fees | NEAR revenue | Capture (bps) | Share of fees | Note |
|---|---|---|---|---|---|---|---|
| 2024-12 | 31 | $2.97M | n/a | n/a | n/a | n/a |  |
| 2025-01 | 31 | $6.41M | n/a | n/a | n/a | n/a |  |
| 2025-02 | 28 | $13.2M | n/a | n/a | n/a | n/a |  |
| 2025-03 | 31 | $23.5M | n/a | n/a | n/a | n/a |  |
| 2025-04 | 30 | $45.3M | n/a | n/a | n/a | n/a |  |
| 2025-05 | 31 | $90.7M | $96 | $0 | 0.00 | 0% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2025-06 | 30 | $184M | $95.4k | $0 | 0.00 | 0% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2025-07 | 31 | $236M | $218k | $0 | 0.00 | 0% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2025-08 | 31 | $332M | $420k | $0 | 0.00 | 0% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2025-09 | 30 | $484M | $713k | $18 | 0.00 | 0% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2025-10 | 31 | $1.72B | $2.5M | $18 | 0.00 | 0% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2025-11 | 30 | $3.66B | $7.76M | $768k | 2.10 | 10% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2025-12 | 31 | $2.01B | $4.12M | $177k | 0.88 | 4% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2026-01 | 31 | $2.72B | $4.41M | $359k | 1.32 | 8% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2026-02 | 28 | $2.38B | $4.13M | $663k | 2.79 | 16% | revenue before 2026-02-23 is treasury sweeps; not used for growth |
| 2026-03 | 31 | $2.08B | $3.59M | $563k | 2.71 | 16% |  |
| 2026-04 | 30 | $1.9B | $3.21M | $259k | 1.36 | 8% |  |
| 2026-05 | 31 | $2B | $3M | $620k | 3.10 | 21% |  |
| 2026-06 | 30 | $2.35B | $3.11M | $619k | 2.63 | 20% |  |
| 2026-07 | 31 | $2.21B | $3.27M | $505k | 2.29 | 15% |  |
| 2026-08 | 31 | $2.78B | $3.84M | $723k | 2.60 | 19% |  |
| 2026-09 | 30 | $4.8B | $7.33M | $1.84M | 3.83 | 25% |  |
| 2026-10 | 31 | $3.99B | $6.39M | $2.19M | 5.49 | 34% |  |
| 2026-11 | 12 | $1.6B | $2.41M | $634k | 3.96 | 26% | partial: through 2026-11-12 |

| # | Claim | Status | Value | Reproduce |
|---|---|---|---|---|
| P2.1 | Revenue per day, trailing 90 d vs the 90 d ending 180 d earlier (2026-02-16 to 2026-05-16; includes days before the 2026-02-23 fee switch) | D+arith | $57.7k vs $13.7k = **x4.22** (+1754%/yr annualized) | `build.py` `growth_at()` |
| P2.2 | Of which: volume | D+arith | x2.17 ($136M vs $62.7M a day) | same windows |
| P2.3 | Of which: capture rate | D+arith | x1.94 (4.24 vs 2.18 bps); 46% of the growth in log terms | revenue / volume |
| P2.4 | Fee switch to buybacks live since 2026-02-23 | D | DefiLlama methodology; [revenue.near.org](https://revenue.near.org/) | `methodology` field |
| P2.5 | Capture rate trend confirmed independently | S | [Nansen Q2 2026](https://nansen.ai/post/nansen-near-quarterly-report-q2-2026): 11.5% lifetime to 30.5% trailing 30 d | - |
| P2.6 | Buyback wallet balance (lower bound on purchases) | M | 2,275,462 NEAR now, 1,974,712 at -30 d; +311,207 over 31 d = 11% of net issuance in the same period | `view_account buybacks.multisignature.near` |

## Pillar 3: The cost of security is falling by design

Net issuance and its dollar cost, month by month, from `total_supply` at archival blocks on the first of each month (cost = NEAR issued x average daily price that month, price from `coins.llama.fi`):

| Month | Supply at start | NEAR issued | Rate/yr | Avg price | Issuance cost | NEAR revenue | Revenue / cost |
|---|---|---|---|---|---|---|---|
| 2025-10 | 1,273,859,405 | 5,041,747 | 4.64% | $2.47 | $12.5M | $18 | 0% |
| 2025-11 | 1,278,901,152 | 2,516,945 | 2.41% | $2.21 | $5.57M | $768k | 14% |
| 2025-12 | 1,281,418,097 | 2,653,983 | 2.42% | $1.60 | $4.24M | $177k | 4% |
| 2026-01 | 1,284,072,080 | 2,578,928 | 2.41% | $1.63 | $4.2M | $359k | 9% |
| 2026-02 | 1,286,651,008 | 2,392,115 | 2.44% | $1.07 | $2.56M | $663k | 26% |
| 2026-03 | 1,289,043,124 | 2,643,777 | 2.43% | $1.28 | $3.37M | $563k | 17% |
| 2026-04 | 1,291,686,900 | 2,626,181 | 2.48% | $1.34 | $3.52M | $259k | 7% |
| 2026-05 | 1,294,313,081 | 2,728,156 | 2.48% | $1.79 | $4.88M | $620k | 13% |
| 2026-06 | 1,297,041,237 | 2,623,835 | 2.47% | $2.17 | $5.68M | $619k | 11% |
| 2026-07 | 1,299,665,072 | 2,721,239 | 2.46% | $1.88 | $5.13M | $505k | 10% |
| 2026-08 | 1,302,386,311 | 2,732,657 | 2.48% | $1.73 | $4.74M | $723k | 15% |
| 2026-09 | 1,305,118,968 | 2,623,096 | 2.46% | $3.19 | $8.38M | $1.84M | 22% |
| 2026-10 | 1,307,742,064 | 2,730,912 | 2.46% | $4.90 | $13.4M | $2.19M | 16% |
| 2026-11 (partial) | 1,310,472,976 | 1,126,926 | 2.49% | $3.82 | $4.31M | $634k | 15% |

| # | Claim | Status | Value | Reproduce |
|---|---|---|---|---|
| P3.1 | Max issuance today | M | 1/40 = 2.5%/yr; treasury share 0/1 (all to stakers; some docs say 90/10, the chain says otherwise) | `EXPERIMENTAL_protocol_config` |
| P3.2 | Realized net supply growth | M | 2.46%/yr (31 d), 2.43%/yr (384 d) | `total_supply` at blocks 219827458, 169975787, 224372730 |
| P3.3 | Security budget | M+arith | 32,251,052 NEAR/yr x $3.58 = **$115M/yr** | P3.2 x price |
| P3.4 | Issuance path | S | 5% to 2.5% (Oct 2025) to **1.6%** passed Nov 2 2026, phased over 24 months after a 90-day grace period | [The Block](https://www.theblock.co/news/defi/2026-11-03-near-governance-approves-token-issuance-432378) |
| P3.5 | Effect on the gap | arith | break-even revenue falls from **$115M to $75.1M/yr** with no growth at all | P3.3 vs P1.3 |

## Pillar 4: The trust layer is hardening (the precondition)

Intents moves real assets across 35+ chains through the Chain Signatures MPC network. If that network fails, the toll road closes. This is why security is the precondition of the bull case, not a side topic.

`v1.signer` state at the first block of each month (FastNEAR archival) and at head:

| Date | Block | Threshold | Participants | Margin | TEE entries | Version | Buyback wallet (NEAR) |
|---|---|---|---|---|---|---|---|
| 2025-10-01 | 166,502,455 | 7 | 10 | 3 | n/a | 2.2.0-rc.1 | n/a |
| 2025-11-01 | 170,879,398 | 7 | 10 | 3 | n/a | 2.2.0-rc.1 | n/a |
| 2025-12-01 | 175,071,646 | 6 | 9 | 3 | 10 | 3.0.2 | n/a |
| 2026-01-01 | 179,388,513 | 6 | 9 | 3 | 10 | 3.0.2 | n/a |
| 2026-02-01 | 183,699,350 | 6 | 9 | 3 | 9 | 3.3.2 | n/a |
| 2026-03-01 | 187,662,387 | 6 | 9 | 3 | 9 | 3.4.1 | n/a |
| 2026-04-01 | 192,071,503 | 5 | 8 | 3 | 9 | 3.7.0 | 40 |
| 2026-05-01 | 196,381,498 | 5 | 8 | 3 | 9 | 3.9.1 | 35,615 |
| 2026-06-01 | 200,826,128 | 6 | 9 | 3 | 11 | 3.10.1 | 263,539 |
| 2026-07-01 | 205,057,938 | 7 | 10 | 3 | 13 | 3.12.0 | 487,255 |
| 2026-08-01 | 209,432,650 | 7 | 11 | 4 | 14 | 3.13.0 | 664,079 |
| 2026-09-01 | 213,788,099 | 9 | 15 | 6 | 15 | 3.14.0 | 941,372 |
| 2026-10-01 | 217,994,521 | 11 | 17 | 6 | 18 | 3.16.0 | 1,847,957 |
| 2026-11-01 | 222,491,355 | 11 | 16 | 5 | 17 | 3.17.0 | 2,144,977 |
| 2026-11-13 | 224,372,730 | 11 | 16 | 5 | 17 | 3.18.0 | 2,275,462 |

| # | Claim | Status | Value | Reproduce |
|---|---|---|---|---|
| P4.1 | MPC threshold history (month starts) | M | 7-of-10 (2025-10) to 6-of-9 (2025-12) to 5-of-8 (2026-04) to 6-of-9 (2026-06) to 7-of-10 (2026-07) to 7-of-11 (2026-08) to 9-of-15 (2026-09) to 11-of-17 (2026-10) to 11-of-16 (2026-11) | archival `v1.signer.state` |
| P4.2 | No admin key on the signing contract | M | 0 access keys; pending code-update votes `{}`; code hash `CpGX8ywXJwvWPgZFDDCTCuPJBHF7BATT51gSfc3APERJ` (not matched to a release build); code changes need threshold votes per `near/mpc` source | `view_access_key_list`; `contract_update_votes` |
| P4.3 | TEE attestation entries | M | 17 entries / 16 accounts for 16 participants (quotes not verified) | `get_tee_accounts` |
| P4.4 | External review | S | Five Trail of Bits audits since Mar 2025, two with high-severity findings (CKD, Robust ECDSA) | [Trail of Bits library](https://trailofbits.com/library/near-one-mpc-chain-signatures/) |
| P4.5 | Base chain | M | 356 validators; 44.95% of supply staked; 10 pools hold > 1/3 of stake | RPC `validators` |
| P4.6 | Incidents in 2026, both outside the signing layer | S | 2026-10-01 NEAR Intents contract: Deposit bug; $3.8M taken, all returned, users made whole ([source](https://thedefiant.io/news/security/near-intents-postmortem-links-3-8-million-exploit-to-deposit-bug)); 2026-11-08 NEAR AI (SGLang): SGLang RCE breach; data only, no funds ([source](https://thehackernews.com/2026/11/sglang-rce-exploit-breaches-near-ai.html)) | `data/incidents.json` |

## The bear case (kept in full)

- **Volume is cyclical, not compounding yet.** Nov 1-12 volume averaged $134M a day, against $129M a day in the same days a year earlier: **+3.6% year on year**. The 90-day year-on-year figure (+212.9%) compares against Intents' 2025 ramp-up (see the monthly table). The six-month surge partly recovers a dip, not a new trend. Last 30 days vs the 30 before: volume -21.6%, fees -29.1%, revenue -19.6%.
- **Capture rate has a ceiling.** 46% of the x4.22 came from NEAR taking more per swap. Gross fees are 15.4 bps; NEAR already keeps 31.6%. Squeezing distribution partners harder risks losing volume to them. From here growth must mostly come from volume.
- **Price works against holders.** Buybacks are paid in dollars, so a higher NEAR price buys fewer NEAR, and the issuance bill in dollars rises. A rally widens the gap unless revenue outruns it.
- **Bought-back NEAR is held, not burned.** The buyback wallet went from 146,161 NEAR 180 days ago to 2,275,462 now, while supply kept growing 2.46% a year. Holders are still diluted today.
- **Lower issuance thins the security budget.** Gross staking yield falls from ~5.5% to ~3.6% at 1.6%. If stakers leave, the base chain weakens exactly when the toll road needs it.
- **Concentrated trust.** 11 of 16 operators can sign on all 8 key domains and redeploy the signing contract with no delay window. Participants went from 17 to 16 in the last 30 days.
- **Two incidents in NEAR-run products in six weeks**, and a TEE did not stop the second.

## What has to be true by 2029-01-31

At today's capture rate of 4.24 bps, revenue of $75.1M/yr needs about **$485M of Intents volume a day, 3.6x today's $136M**. Equivalent paths: volume x2.5 with capture at 6 bps, or volume x3.6 with capture flat. Anything that holds that path for 27 months while the signing layer stays clean makes NEAR a long-term hold on these terms.

## Tripwires (pre-registered in `d5491d7`)

| ID | Watch | Now | Bear trigger | Bull trigger | State | Detail |
|---|---|---|---|---|---|---|
| T1 | Captured revenue, trailing 90 d vs the 90 d ending 180 d earlier, annualized | +1754%/yr (x4.22 in 6 mo) | < 75%/yr at 2 quarter-ends running | >= 75%/yr at 4 quarter-ends running | **neither** | quarter-ends: 2025-12-31 n/a, 2026-03-31 > +10000%, 2026-06-30 +151%, 2026-09-30 +260% (n/a = no revenue data that far back) |
| T2 | Intents volume, 90 d, year on year | +212.9% (month to date +3.6%) | < 0% at 2 quarter-ends running | > 50% | **BULL** | quarter-ends: 2025-12-31 n/a, 2026-03-31 > +10000%, 2026-06-30 +1816%, 2026-09-30 +825%; year-earlier windows fall in Intents' 2025 ramp-up, which inflates this |
| T3 | Revenue coverage of issuance (run-rate / security budget) | 18% | falls 3 month-ends running | >= 50% | **neither** | month-end coverage: 2025-10 0%, 2025-11 5%, 2025-12 8%, 2026-01 11%, 2026-02 14%, 2026-03 16%, 2026-04 14%, 2026-05 10%, 2026-06 9%, 2026-07 12%, 2026-08 13%, 2026-09 12%, 2026-10 12% |
| T4 | Staked share of supply during the HSP-029 ramp | 44.95% | < 40% | >= 45% held through ramp | **neither** | ramp 2027-01-31 to 2029-01-31; 0 snapshots in ramp so far |
| T5 | MPC liveness margin (participants - threshold) | 5 (11-of-16) | < 4, or threshold < 9 | >= 7 | **neither** |  |
| T6 | Loss traced to the MPC signing layer | 0 | any -> thesis VOID | - | **neither** | from data/incidents.json (layer = mpc_signing) |
| T7 | User loss not made whole in NEAR-run products, last 90 d | 0 | >= 1 | - | **neither** | from data/incidents.json |

**Verdict rule.** HOLD when T1 and T3 bull triggers both fire with no bear trigger. VOID if T6 fires. DON'T HOLD if two bear triggers fire. Otherwise ON TRACK, UNPROVEN.

**Dated predictions:**

| By | Prediction | Now | State |
|---|---|---|---|
| 2027-03-31 | trailing-90-day revenue >= $80k/day | $57.7k/day | pending, behind |
| 2027-03-31 | volume YoY > 0% | +212.9% | pending, on course |
| 2027-03-31 | MPC threshold >= 11 | 11 | pending, on course |
| 2027-03-31 | MPC participants >= 16 | 16 | pending, on course |
| 2027-03-31 | staked share >= 42% | 44.95% | pending, on course |

## Optional upside, not counted

NEAR AI (confidential inference used by Brave Leo, 1M+ NEAR staked to pay for inference) is real usage, but none of its revenue is shown reaching the buyback wallet, and stake-for-inference spends staking rewards rather than adding revenue. It is excluded from the case until that changes.

## What this thesis cannot prove

Price targets; total value secured by MPC keys (DefiLlama's $181M Intents TVL is only a floor); whether high audit findings are fixed in deployed 3.18.0; whether the deployed code hash matches a tagged `near/mpc` release; validity of TEE quotes; whether solvers would accept a higher NEAR take rate. The buyback wallet balance is a lower bound on purchases (transfers out are not traced). Stake history starts at this repo's first snapshot, because `validators` at past blocks is not served by archival nodes. Incidents (T6, T7) are entered by hand in `data/incidents.json` with sources.

## Status key and sourcing

**M** = measured on NEAR mainnet or FastNEAR archival RPC · **D** = DefiLlama public API · **S** = primary source or established outlet · arith = computed here from M/D values. No other hackathon entry is cited as evidence.
