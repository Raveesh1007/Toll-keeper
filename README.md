# NEAR investment thesis, reproducible

Built at NEAR HACKATHON, Investment Thesis track. The thesis is [`THESIS.md`](THESIS.md). Every number tagged **M** (NEAR mainnet / archival RPC) or **D** (DefiLlama) in it is computed by `build.py` from raw files that `collect.py` fetches. The tripwires and verdict rule in [`config/tripwires.json`](config/tripwires.json) were committed before the first data run (commit `d5491d7`); `build.py` prints a warning into THESIS.md if that file is ever edited afterwards.

Current verdict and every number: [`THESIS.md`](THESIS.md) · dashboard: `site/index.html` (hosted on GitHub Pages) · machine-readable: [`data/metrics.json`](data/metrics.json).

Other project by the same author at this hackathon: **TODO: name + URL** (Q-015).

## Requirements

Python 3.11+, standard library only. No API keys, no `pip install`. Network access to `rpc.mainnet.near.org`, `archival-rpc.mainnet.fastnear.com`, `api.llama.fi`, `coins.llama.fi`, `api.coingecko.com`.

## Do X → see Y

1. `python collect.py` → takes about 2 minutes, prints one line per archival block, ends with `wrote data/raw/<YYYY-MM-DD>/ (block N)`. That directory holds `head.json`, `history.json`, `defillama.json`, `price.json`.
2. `python build.py` → prints `VERDICT: ...`, one line per tripwire T1-T7 with its state, and the key metrics. Rewrites `THESIS.md` (from `THESIS.template.md`), `data/metrics.json`, `data/history.csv`, `site/metrics.json`, `site/metrics.js`. It uses the newest `data/raw/<date>/`; skip step 1 to rebuild from the committed raw data.
3. Open `site/index.html` in a browser (double-click works; no server needed) → the verdict banner, block height and numbers match the `build.py` output and `THESIS.md`.
4. Run `python build.py` again, then `git status --short` → no changes. The build is deterministic for the same raw files.
5. `python test_build.py` → prints `ok` (checks the window averaging, formatting and MPC-state parsing).
6. Check two numbers by hand against `THESIS.md` (results move with the chain, so compare to a fresh `collect.py` run):

   Total supply (P3.x; yoctoNEAR, divide by 1e24):
   ```
   curl -s https://rpc.mainnet.near.org -H 'Content-Type: application/json' \
     -d '{"jsonrpc":"2.0","id":1,"method":"block","params":{"finality":"final"}}' \
     | python -c "import json,sys;h=json.load(sys.stdin)['result']['header'];print(h['height'],int(h['total_supply'])/1e24)"
   ```
   MPC threshold and participants (P4.1, T5):
   ```
   curl -s https://rpc.mainnet.near.org -H 'Content-Type: application/json' \
     -d '{"jsonrpc":"2.0","id":1,"method":"query","params":{"request_type":"call_function","finality":"final","account_id":"v1.signer","method_name":"state","args_base64":"e30="}}' \
     | python -c "import json,sys;p=json.loads(bytes(json.load(sys.stdin)['result']['result']))['Running']['parameters'];print(p['threshold'],'of',len(p['participants']['participants']))"
   ```
   For a past block, use `https://archival-rpc.mainnet.fastnear.com` and replace `"finality":"final"` with `"block_id":<height>` (heights are in `data/raw/<date>/history.json`).

## What runs where

| File | Does |
|---|---|
| `collect.py` | Fetches head state (supply, validators, protocol config, `v1.signer` state/version/TEE/votes/keys, buyback wallet), the same fields at archival blocks 30/31/90/180/365/384 days back and on the 1st of every month since 2025-10, DefiLlama daily volume/fees/revenue and TVL, CoinGecko spot price and DefiLlama daily price. 3 tries, 2 s apart, per HTTP call. |
| `build.py` | Computes every metric, the monthly tables, tripwires, verdict, dated predictions and claim register; renders `THESIS.md`. Asserts that the seed files in `data/defillama/` are an exact subset of the live DefiLlama series. |
| `config/tripwires.json` | Pre-registered thresholds, verdict rule, predictions. Frozen. |
| `data/incidents.json` | Hand-entered, sourced incidents; the only input for T6 and T7 (not measurable on chain). |
| `site/index.html` | Static dashboard, vanilla JS, reads `metrics.js` (same content as `metrics.json`). |
| `.github/workflows/refresh.yml` | Daily 01:17 UTC: collect → test → build → commit → deploy `site/` to GitHub Pages. Needs Settings → Pages → Source: GitHub Actions. |

## Method notes

- History blocks are chosen by timestamp (estimate from block rate, one correction step), so "31 d" is 31 days of wall time, and issuance is annualized by the real seconds between blocks.
- Revenue growth compares the trailing 90 days with the 90 days ending 180 days earlier, clipped so no day before 2026-03-01 is used (DefiLlama revenue before the 2026-02-23 fee switch is lumpy treasury sweeps). The clipped window length is printed in claim P2.1.
- Year-on-year volume is reported two ways: month-to-date vs the same days a year earlier, and 90 days vs the same 90 days a year earlier (T2). They differ a lot right now because Intents was still ramping up in 2025; both are shown.
- Validator stake at past blocks is not served by archival nodes, so stake history (T4) starts at this repo's first snapshot (`data/history.csv`).
- On Windows, `collect.py` builds its TLS context from the Windows ROOT store only, because the intermediate store can hold an expired ISRG cross-signature that makes Python reject FastNEAR's valid certificate. Verification stays on.

## AI disclosure (Q-005)

`collect.py`, `build.py`, `test_build.py`, `site/index.html`, `.github/workflows/refresh.yml`, `THESIS.template.md` (adapted from the author's draft) and this README were written with an AI coding assistant. The thesis argument, the tripwire design and the data-source choices are the author's.

## License

MIT, see [`LICENSE`](LICENSE).
