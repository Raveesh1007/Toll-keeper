<!-- WEAKNESSES.md is generated from WEAKNESSES.template.md by `python build.py`. Edit the template, not WEAKNESSES.md. -->
# Known weaknesses

> **Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire.**

Limits only. Numbers are filled in by `build.py` from the same data as `data/metrics.json` (data as of {asof}, block {height}).

1. **T1 artifact quarters.** Before the validity rule, {voided_n} T1 quarter-ends compared against windows that start before the fee switch: {voided_q}. Revenue before the switch was near zero, so these ratios are inflated by construction. `build.py` now marks them `n/a` ("{t1_rule}"); valid quarter-ends so far: {t1_valid_n}; next evaluated {t1_next_q}. The same problem affects the 6-month ×{g6} figure (earlier window from {g6_start}), which is kept only as a detail (THESIS claim P2.4). → `data/metrics.json` → `t1_validity`, `tripwires[T1]`.
2. **T2 base effect.** 90-day year-on-year volume is {vol_yoy_90}, because its comparison window falls in Intents' 2025 ramp-up. Month-to-date year on year is {vol_yoy_mtd}, which matches the "volume flat" bear case. T2 still fires its bull trigger on the 90-day figure, as pre-registered. → `metrics.vol_yoy_90d`, `metrics.vol_yoy_mtd`.
3. **T3 has two measures.** Run-rate (trailing 90-day average × 365): {coverage}. Month-end series (trigger input): {cov_me_last} for {cov_me_month}. The bear trigger uses the month-end series; the bull trigger uses the run-rate. → `metrics.coverage_usd`, `metrics.coverage_month_end_latest`, `tripwires[T3]`.
4. **Revenue growth is not all new demand.** {headline_growth}: volume ×{hg_vol}, capture rate ×{hg_cap}. Monthly revenue is noisy month to month. → `headline_growth`, `metrics.headline_growth_*`.
5. **DefiLlama is a third party and revises recent days.** Fee and revenue definitions are DefiLlama's, and values for the latest days change after a snapshot is taken. → `data/derived/drift.json`, [METHODS.md](METHODS.md).
6. **Pre-registration proof has limits.** Git commit dates are set by the author. A GitHub Actions run is timestamped by GitHub's servers and shows that a commit existed by that time, not when it was written. → [PROVENANCE.md](PROVENANCE.md).
7. **Value secured is context, not exposure.** DefiLlama's Intents TVL ({tvl}) is only partly controlled by MPC signers; that share is not measured. → `data/derived/security.json` → `value_in_intents_usd`.
8. **The bond finding has a narrow scope.** The participant-bond result covers only the contract version and source files cited in it. → `data/derived/security.json` → `participant_bond`.
9. **Incidents: n = {n_incidents}.** Net recorded user loss is {net_loss}. That is a record of {n_incidents} events, not a rate or a forecast. → `data/incidents.json`.
10. **NEAR AI is excluded from the verdict.** Its revenue is not shown reaching NEAR holders, so AI adoption does not count toward the thesis.
