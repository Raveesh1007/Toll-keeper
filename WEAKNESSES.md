<!-- WEAKNESSES.md is generated from WEAKNESSES.template.md by `python build.py`. Edit the template, not WEAKNESSES.md. -->
# Known weaknesses

> **Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire.**

Limits only. Numbers are filled in by `build.py` from the same data as `data/metrics.json` (data as of 2026-11-14, block 224,469,621).

1. **T1 artifact quarters.** Before the validity rule, 3 T1 quarter-ends compared against windows that start before the fee switch: 2026-03-31 (> +10000%/yr, window from 2025-07-05), 2026-06-30 (+151%/yr, window from 2025-10-04), 2026-09-30 (+260%/yr, window from 2026-01-04). Revenue before the switch was near zero, so these ratios are inflated by construction. `build.py` now marks them `n/a` ("comparison window predates fee switch (Mar 2026)"); valid quarter-ends so far: 0; next evaluated 2026-12-31. The same problem affects the 6-month ×4.23 figure (earlier window from 2026-02-17), which is kept only as a detail (THESIS claim P2.4). → `data/metrics.json` → `t1_validity`, `tripwires[T1]`.
2. **T2 base effect.** 90-day year-on-year volume is +207.2%, because its comparison window falls in Intents' 2025 ramp-up. Month-to-date year on year is +5.9%, which matches the "volume flat" bear case. T2 still fires its bull trigger on the 90-day figure, as pre-registered. → `metrics.vol_yoy_90d`, `metrics.vol_yoy_mtd`.
3. **T3 has two measures.** Run-rate (trailing 90-day average × 365): 20%. Month-end series (trigger input): 12% for Oct 2026. The bear trigger uses the month-end series; the bull trigger uses the run-rate. → `metrics.coverage_usd`, `metrics.coverage_month_end_latest`, `tripwires[T3]`.
4. **Revenue growth is not all new demand.** x3.9 from Mar 2026 to Oct 2026 (monthly revenue), of which about 52% is capture-rate expansion: volume ×1.92, capture rate ×2.03. Monthly revenue is noisy month to month. → `headline_growth`, `metrics.headline_growth_*`.
5. **DefiLlama is a third party and revises recent days.** Fee and revenue definitions are DefiLlama's, and values for the latest days change after a snapshot is taken. → `data/derived/drift.json`, [METHODS.md](METHODS.md).
6. **Pre-registration proof has limits.** Git commit dates are set by the author. A GitHub Actions run is timestamped by GitHub's servers and shows that a commit existed by that time, not when it was written. → [PROVENANCE.md](PROVENANCE.md).
7. **Value secured is context, not exposure.** DefiLlama's Intents TVL ($169M) is only partly controlled by MPC signers; that share is not measured. → `data/derived/security.json` → `value_in_intents_usd`.
8. **The bond finding has a narrow scope.** The participant-bond result covers only the contract version and source files cited in it. → `data/derived/security.json` → `participant_bond`.
9. **Incidents: n = 2.** Net recorded user loss is $0. That is a record of 2 events, not a rate or a forecast. → `data/incidents.json`.
10. **NEAR AI is excluded from the verdict.** Its revenue is not shown reaching NEAR holders, so AI adoption does not count toward the thesis.
