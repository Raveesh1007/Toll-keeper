// JS model (site/model.js) vs Python (build.py, via data/metrics.json) on today's defaults, to 4 significant figures.
// Run: node test_model.js   (test_build.py runs it automatically when node is installed)
const {tollModel, tollDefaults} = require("./site/model.js");
const M = require("./data/metrics.json").metrics;
const o = tollModel(tollDefaults(M));
let bad = 0;
const check = (name, js, py) => {
  const ok = Math.abs(js - py) <= 5e-4 * Math.abs(py);
  bad += !ok;
  console.log(`${ok ? "ok      " : "MISMATCH"} ${name}: js ${js.toPrecision(6)} vs py ${py.toPrecision(6)}`);
};
check("break-even volume/day", o.breakevenVolPerDay, M.breakeven_vol_per_day);
check("required CAGR", o.requiredCagr, M.required_cagr);
check("revenue run-rate", o.runRate, M.revenue_run_rate);
check("coverage at target issuance", o.coverage, M.revenue_run_rate / M.security_budget_target_usd);
check("cost at target issuance", o.cost, M.security_budget_target_usd);
process.exit(bad ? 1 : 0);
