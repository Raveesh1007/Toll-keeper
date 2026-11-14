<div align="center">

# Toll-keeper

**Can NEAR's tolls pay for its road?**
A NEAR investment thesis where every number is computed from public data, re-checked daily, and judged by alarms written down in advance.

[**Live dashboard**](https://raveesh1007.github.io/Toll-keeper/) · [Thesis](THESIS.md) · [Live numbers (JSON)](data/metrics.json) · [Pre-registered alarms](config/tripwires.json)

`Python 3.11+` · `standard library only` · `no API keys` · `MIT`

</div>

---

## For judges and AI reviewers: start here

About 5 minutes. You need Python 3.11+, git and internet access. Nothing to install, no keys.

| Step | Run | Expected result |
|---|---|---|
| 1 | `git clone https://github.com/Raveesh1007/Toll-keeper.git && cd Toll-keeper` | Repo cloned. |
| 2 | `python test_build.py` | Prints `ok`. |
| 3 | `python build.py` | Works offline from the committed raw data. The first line starts with `VERDICT:` (today `ON TRACK, UNPROVEN`), then one line each for T1 to T7, then key metrics. Exit code 0. |
| 4 | `git status --short` | Empty. The build is deterministic, so re-running it changes no files. |
| 5 | `python collect.py` | About 2 minutes. Ends with `wrote data/raw/<YYYY-MM-DD>/ (block N)`. Fetches live data; no errors. |
| 6 | `python build.py` | Same format as step 3. Numbers move slightly because the chain has moved. `THESIS.md` and `site/metrics.json` are rewritten. |
| 7 | Run the two `curl` commands under [Check two numbers by hand](#check-two-numbers-by-hand) | Total supply is about 1.31 billion NEAR; MPC is `11 of 16` (it may differ if the network changed). Same as `data/metrics.json`. |
| 8 | `git log --reverse --oneline -- config/tripwires.json` | One commit (`d5491d7`), and `git log --reverse --oneline \| head -1` is the same commit: the alarms were committed before any data run. |
| 9 | Open the [live dashboard](https://raveesh1007.github.io/Toll-keeper/) | Verdict, block height and numbers match `data/metrics.json` (for the same data date). |
| 10 | Open the repo's Actions tab | Workflow `refresh` runs daily at 01:17 UTC; its commits are named `data refresh YYYY-MM-DD`. |

**What to judge**
- **Reproducible:** every **M** and **D** number in [`THESIS.md`](THESIS.md) is written by `build.py` from `data/raw/`. Search the thesis for a number, then find it in `data/metrics.json` or the claim register on the dashboard.
- **Falsifiable:** seven alarms and a verdict rule are fixed in [`config/tripwires.json`](config/tripwires.json). `build.py` flags any edit made after the first commit.
- **Honest limits:** the thesis lists what it cannot prove, and keeps the bear case in full.

**Known limits, so you don't mistake them for bugs**
- T6 and T7 (losses) read `data/incidents.json`, which is entered by hand with sources, because they can't be measured on chain.
- Stake history (T4) starts at this repo's first snapshot; archival nodes don't serve past stake.
- **T1 (revenue growth):** a comparison only counts if its earlier window starts on or after 2026-03-01 (validity rule added 2026-11-14, after pre-registration; reason: "comparison window predates fee switch (Mar 2026)"). Valid quarter-ends so far: 0, qualifying: 0; the next one evaluated is 2026-12-31. Current values: `metrics.json` → `t1_validity`.
- **T2 (volume) base effect:** 90-day year-on-year volume (+207.2%) compares against Intents' 2025 ramp-up; month-to-date year on year is +5.9%. The threshold and state logic are unchanged.
- **T3 (coverage) has two labelled measures:** run-rate (trailing 90-day average × 365): 20%, and month-end series (trigger input): 12% for 2026-10. The bear trigger reads the month-end series.
- How coverage and break-even are computed, and how break-even moves under other inputs: [METHODS.md](METHODS.md).
- Live numbers change daily, so values in the README tables are a snapshot, not a test target.

## The thesis in 30 seconds

NEAR runs a service that swaps coins between blockchains, and it keeps a small fee on every swap. NEAR also creates new NEAR coins every year to pay the computers that keep the network running. More coins in circulation makes each existing coin a little less valuable.

**The bet:** if the money NEAR earns from swaps grows big enough to buy back as many coins as NEAR creates, owners stop losing value to the new coins, and holding NEAR for years makes sense. This repo checks every day whether that is happening.

| | Today | Needed by early 2029 |
|---|---|---|
| Revenue NEAR keeps (yearly pace) | ~$21M | ~$75M |
| Cost of new tokens printed | ~$115M | ~$75M (after the Nov 2026 issuance cut) |
| Coverage | **18%** | 100% |
| Daily swap volume | ~$136M | ~$485M |
| Signing network (MPC) | 11-of-16 | no loss in the signing layer |

Verdict today: **ON TRACK, UNPROVEN.** Figures above are a snapshot; `THESIS.md` and `data/metrics.json` always hold the current ones.

## How it works

```
 NEAR RPC ─┐
 FastNEAR  ├─► collect.py ─► data/raw/<date>/ ─► build.py ─┬─► THESIS.md   (numbers + verdict)
 DefiLlama │                                               ├─► data/metrics.json, history.csv
 CoinGecko ┘                                               └─► site/  (dashboard, GitHub Pages)
                                  config/tripwires.json ──► (frozen before the first data run)
```

Every figure tagged **M** (measured on NEAR mainnet) or **D** (DefiLlama) in the thesis comes out of `build.py`. Nothing is typed in by hand.

## Quick start: do X → see Y

| # | Do | See |
|---|---|---|
| 1 | `python collect.py` | About 2 minutes. Ends with `wrote data/raw/<YYYY-MM-DD>/ (block N)`; that folder holds `head.json`, `history.json`, `defillama.json`, `price.json`. |
| 2 | `python build.py` | Prints `VERDICT: ...`, one line per tripwire T1-T7, and the key metrics. Rewrites `THESIS.md`, `data/metrics.json`, `data/history.csv`, `site/metrics.js`, `site/metrics.json`. Uses the newest `data/raw/<date>/`, so you can skip step 1 to rebuild from committed data. |
| 3 | Open the [live dashboard](https://raveesh1007.github.io/Toll-keeper/), or `site/index.html` locally | The dashboard shows the same verdict, block height and numbers as step 2. No server needed. |
| 4 | `python build.py` again, then `git status --short` | No changes: the build is deterministic for the same raw files. |
| 5 | `python test_build.py` | `ok` |
| 6 | Hand-check two numbers (below) | They match a fresh `collect.py` run. |

### Check two numbers by hand

On Windows run these in **Git Bash**, not PowerShell.

<details>
<summary>Total supply (yoctoNEAR ÷ 1e24)</summary>

```bash
curl -s https://rpc.mainnet.near.org -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"block","params":{"finality":"final"}}' \
  | python -c "import json,sys;h=json.load(sys.stdin)['result']['header'];print(h['height'],int(h['total_supply'])/1e24)"
```
</details>

<details>
<summary>MPC threshold and participants (claim P4.1, alarm T5)</summary>

```bash
curl -s https://rpc.mainnet.near.org -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"query","params":{"request_type":"call_function","finality":"final","account_id":"v1.signer","method_name":"state","args_base64":"e30="}}' \
  | python -c "import json,sys;p=json.loads(bytes(json.load(sys.stdin)['result']['result']))['Running']['parameters'];print(p['threshold'],'of',len(p['participants']['participants']))"
```
</details>

For a past block use `https://archival-rpc.mainnet.fastnear.com` and replace `"finality":"final"` with `"block_id":<height>` (heights are in `data/raw/<date>/history.json`).

## What's in the repo

| Path | Purpose |
|---|---|
| [`THESIS.md`](THESIS.md) | The thesis. Generated from `THESIS.template.md`; edit the template, not this file. |
| `collect.py` | Fetches chain state now and at past blocks (30/31/90/180/365/384 days back and the 1st of each month since 2025-10), DefiLlama daily volume/fees/revenue/TVL, and NEAR price. Calls are paced (0.25 s apart) and retried up to 6 times, backing off on HTTP 429 rate limits. |
| `build.py` | Computes every metric, monthly table, tripwire state, verdict and dated prediction, then writes the outputs above. |
| [`config/tripwires.json`](config/tripwires.json) | Seven alarms, the verdict rule and the dated predictions. Frozen in commit `d5491d7` before any data was collected; `build.py` flags any later edit in `THESIS.md`. |
| `data/incidents.json` | Hand-entered, sourced incidents. The only input for T6 and T7, which can't be measured on chain. |
| `data/defillama/` | Seed copies of the daily volume and revenue series; `build.py` asserts they match the live data for every day except the latest 7 (DefiLlama revises recent days). |
| `site/index.html` | Static dashboard, vanilla JS, light and dark mode. Reads `site/metrics.js`. |
| `.github/workflows/refresh.yml` | Daily 01:17 UTC: collect, test, build, commit, deploy `site/` to GitHub Pages. |

## The alarms and the verdict

| ID | Watches | Warning fires when |
|---|---|---|
| T1 | Revenue growth (90 days vs 90 days ending 180 days earlier, annualized) | under 75%/yr at two quarter-ends in a row |
| T2 | Swap volume, 90 days year on year | below 0% for two quarters |
| T3 | Revenue ÷ cost of new tokens | falls three month-ends in a row |
| T4 | Staked share of supply | under 40% |
| T5 | MPC margin (participants − threshold) | under 4, or threshold under 9 |
| T6 | Loss traced to the MPC signing layer | any loss voids the thesis |
| T7 | User loss not made whole, last 90 days | one or more |

**Verdict rule:** `VOID` if T6 fires; `DON'T HOLD` if two warnings fire; `HOLD` if the T1 and T3 good-sign triggers both fire with no warning; otherwise `ON TRACK, UNPROVEN`.

## Setup on GitHub

1. Settings → Actions → General → Workflow permissions: **Read and write**.
2. Settings → Pages → Source: **GitHub Actions**.
3. Actions tab → `refresh` → Run workflow once to confirm.

## Method notes

- Archival data comes from FastNEAR, falling back to NEAR's own archival node if FastNEAR refuses (it rate-limits GitHub's shared runners). First-of-month points never change, so they are reused from the previous snapshot instead of re-fetched; if both archives refuse, the moving points (-30 d etc.) reuse the previous snapshot's blocks and are marked `"stale": true` in `history.json`.
- History blocks are chosen by timestamp, so "31 days" is 31 days of wall time, and issuance is annualized by the real seconds between blocks.
- Revenue growth compares the trailing 90 days with the full 90 days ending 180 days earlier. That earlier window starts 2026-02-16, so it includes a few days before the 2026-02-23 fee switch, when DefiLlama revenue was lumpy treasury sweeps. Claim P2.1 prints the exact window.
- Year-on-year volume is reported two ways, month-to-date and 90 days. They differ a lot because Intents was still ramping up in 2025; both are shown.
- Validator stake at past blocks isn't served by archival nodes, so stake history (T4) starts at this repo's first snapshot (`data/history.csv`).
- On Windows, `collect.py` builds its TLS context from the Windows ROOT store only, because the intermediate store can hold an expired ISRG cross-signature that makes Python reject FastNEAR's valid certificate. Verification stays on.
- The dashboard loads the Onest font from a public CDN; without network it renders with a fallback font.
- Network access needed: `rpc.mainnet.near.org`, `archival-rpc.mainnet.fastnear.com`, `api.llama.fi`, `coins.llama.fi`, `api.coingecko.com`.

## Hackathon

Built at NEAR HACKATHON, Investment Thesis track.

- **Other project by the same author at this hackathon (Q-015):** **Inferents**: repo https://github.com/Raveesh1007/Inferents · demo https://inferents.vercel.app
- **AI disclosure (Q-005):** `collect.py`, `build.py`, `test_build.py`, `site/index.html`, `.github/workflows/refresh.yml`, `THESIS.template.md` (adapted from the author's draft) and this README were written with an AI coding assistant. The thesis argument, the tripwire design and the data-source choices are the author's.

Not investment advice.

