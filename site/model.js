// "Run the model": the same formulas as build.py, so the sliders and the thesis agree.
// Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire.
//   run-rate              = volume/day × capture × 365
//   cost                  = issuance rate × total supply × NEAR price
//   coverage              = run-rate ÷ cost
//   break-even volume/day = cost ÷ 365 ÷ capture
//   required CAGR         = (cost ÷ run-rate)^(12 ÷ months to the full cut) − 1
function tollModel(i) {
  const capture = i.captureBps / 1e4;
  const runRate = i.volumePerDay * capture * 365;
  const cost = i.issuanceRate * i.supply * i.price;
  return {runRate, cost, coverage: runRate / cost, breakevenVolPerDay: cost / 365 / capture,
          requiredCagr: Math.pow(cost / runRate, 12 / i.months) - 1};
}

function tollDefaults(M) {
  return {volumePerDay: M.volume_per_day_t90, captureBps: M.capture_bps_t90, price: M.price_usd,
          issuanceRate: M.target_issuance, supply: M.total_supply, months: M.months_to_full_cut};
}

if (typeof module !== "undefined") module.exports = {tollModel, tollDefaults};
