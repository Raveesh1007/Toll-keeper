"""data/raw/<latest>/ -> data/metrics.json, data/history.csv, site/metrics.json, site/metrics.js, THESIS.md.
Standard library only. Deterministic: same raw files + config + git history -> same outputs."""
import csv, datetime as dt, glob, json, math, os, subprocess, sys

DAY = dt.timedelta(1)
YOCTO = 1e24
YEAR_S = 365 * 86400
OPS = {"<": lambda a, b: a < b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def day(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).date()


def window(s, end, n, start=None):
    """Mean of daily series s over the n days ending at `end` (inclusive), optionally clipped at `start`."""
    days = [end - DAY * i for i in range(n) if start is None or end - DAY * i >= start]
    return (sum(s.get(d, 0) for d in days) / len(days), len(days)) if days else (None, 0)


def months(first, last):
    m = first.replace(day=1)
    while m <= last:
        yield m
        m = dt.date(m.year + m.month // 12, m.month % 12 + 1, 1)


def mpc(state):
    if not state:
        return None
    kind, s = next(iter(state.items()))
    p = s.get("parameters") or (s.get("previous_running_state") or {}).get("parameters")
    if not p:
        return {"kind": kind}
    ids = [e[0] if isinstance(e, list) else e for e in p["participants"]["participants"]]
    return {"kind": kind, "threshold": p["threshold"], "participants": len(ids), "ids": ids,
            "domains": len((s.get("domains") or {}).get("domains", []))}


def supply(p):
    return int(p["total_supply"]) / YOCTO


def secs(p):
    return int(p["timestamp_ns"]) / 1e9


def per_year(a, b, value_a, value_b):
    return (value_b - value_a) * YEAR_S / (secs(b) - secs(a))


def git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return ""


# ---- formatting (all outputs go through these, so rounding is consistent) ----
def usd(x):
    if x is None:
        return "n/a"
    for div, unit in ((1e9, "B"), (1e6, "M"), (1e3, "k"), (1, "")):
        if abs(x) >= div * 0.9995 or div == 1:
            s = f"{x / div:.3g}"
            return f"${s}{unit}" if "e" not in s else f"${x / div:.0f}{unit}"


def pct(x, d=1, sign=False):
    return "n/a" if x is None else f"{x * 100:{'+' if sign else ''}.{d}f}%"


def num(x):
    return f"{x:,.0f}"


def bps(x):
    return "n/a" if x is None else f"{x * 1e4:.2f}"


def mult(x):
    return "n/a" if x is None else f"{x:.2f}"


def r(x, n=6):
    return None if x is None else round(x, n)


def table(header, rows):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] +
                     ["| " + " | ".join(str(c) for c in row) + " |" for row in rows])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = load("config/tripwires.json")
    C = cfg["constants"]
    clean = dt.date.fromisoformat(C["clean_data_start"])
    full_cut = dt.date.fromisoformat(C["full_cut_date"])
    ramp_start = dt.date.fromisoformat(C["ramp_start"])
    raw_dirs = sorted(glob.glob("data/raw/*/"))
    if not raw_dirs:
        sys.exit("no data/raw/<date>/ found: run python collect.py first")
    raw = raw_dirs[-1]
    head, hist = load(raw + "head.json"), load(raw + "history.json")
    llama, price_raw = load(raw + "defillama.json"), load(raw + "price.json")
    incidents = load("data/incidents.json")
    P = {p["label"]: p for p in hist}

    # ---------- DefiLlama ----------
    vol = {day(t): v for t, v in llama["volume"]["totalDataChart"]}
    fees = {day(t): v for t, v in llama["fees"]["totalDataChart"]}
    rev = {day(t): v for t, v in llama["revenue"]["totalDataChart"]}
    for name, s in (("revenue", rev), ("volume", vol)):  # seed files must match settled history; DefiLlama revises the latest days
        seed = {day(t): v for t, v in load(f"data/defillama/intents_{name}_daily.json")}
        settled = max(s) - 7 * DAY
        assert all(s.get(d) == v for d, v in seed.items() if d <= settled), f"seed {name} disagrees with live DefiLlama before {settled}"
    E = min(max(vol), max(fees), max(rev))  # last complete day in all three series

    def total(s, end, n):
        return sum(s.get(end - DAY * i, 0) for i in range(n))

    vol30, fees30, rev30 = total(vol, E, 30), total(fees, E, 30), total(rev, E, 30)
    vol30p, fees30p, rev30p = (total(s, E - 30 * DAY, 30) for s in (vol, fees, rev))
    vol365 = total(vol, E, 365)

    def growth_at(end):
        # full 90-day windows, no March cutoff (author's choice, 2026-11-13; same method as draft 3)
        cur, _ = window(rev, end, 90)
        pri, n = window(rev, end - 180 * DAY, 90)
        if end - 269 * DAY < min(rev) or not pri:
            return None
        vc, _ = window(vol, end, 90)
        vp, _ = window(vol, end - 180 * DAY, 90)
        g = cur / pri
        return {"end": end, "rev": cur, "rev_prior": pri, "prior_days": n, "vol": vc, "vol_prior": vp,
                "ratio": g, "annualized": g ** (365 / 180) - 1, "vol_ratio": vc / vp,
                "cap": cur / vc, "cap_prior": pri / vp, "cap_ratio": (cur / vc) / (pri / vp)}

    def vol_yoy_90(end):
        prev = [end - DAY * (365 + i) for i in range(90)]
        if not all(d in vol for d in prev):
            return None
        return total(vol, end, 90) / sum(vol[d] for d in prev) - 1

    G = growth_at(E)
    t90_rev, t90_vol = window(rev, E, 90)[0], window(vol, E, 90)[0]
    capture = t90_rev / t90_vol
    mtd = [E.replace(day=d) for d in range(1, E.day + 1)]
    vol_yoy_mtd = sum(vol[d] for d in mtd) / sum(vol[d.replace(year=d.year - 1)] for d in mtd) - 1
    mtd_now, mtd_prev = sum(vol[d] for d in mtd) / len(mtd), sum(vol[d.replace(year=d.year - 1)] for d in mtd) / len(mtd)
    yoy90 = vol_yoy_90(E)

    # ---------- chain ----------
    S = supply(head)
    price = price_raw["spot_usd"]
    prices = {day(p["timestamp"]): p["price"] for p in price_raw["daily"]}
    stakes = sorted((int(v["stake"]) / YOCTO for v in head["validators"]["current"]), reverse=True)
    staked = sum(stakes)
    cum, nakamoto = 0, 0
    for nakamoto, st in enumerate(stakes, 1):
        cum += st
        if cum > staked / 3:
            break
    mi, tr = head["protocol_config"]["max_inflation_rate"], head["protocol_config"]["protocol_reward_rate"]
    M = mpc(head["mpc_state"])
    tee = head["tee_accounts"] or []
    bb = lambda p: int(p["buyback"]["amount"]) / YOCTO if p.get("buyback") else None
    iss31 = per_year(P["-31d"], head, supply(P["-31d"]), S)
    iss384 = per_year(P["-384d"], head, supply(P["-384d"]), S)
    budget = iss31 * price
    budget_target = C["target_issuance"] * S * price
    run_rate = t90_rev * 365
    coverage = run_rate / budget
    d_supply31 = S - supply(P["-31d"])
    d_bb31 = bb(head) - bb(P["-31d"])
    months_left = (full_cut - E).days / 30.4375
    required_cagr = (budget_target / run_rate) ** (12 / months_left) - 1
    be_vol = budget_target / 365 / capture
    vol_x_at_6bps = budget_target / 365 / 0.0006 / t90_vol

    # ---------- monthly tables ----------
    monthly = []
    for m in months(min(vol), E):
        ds = [d for d in (m + DAY * i for i in range(31)) if d.month == m.month and d <= E]
        v = sum(vol.get(d, 0) for d in ds)
        f = sum(fees.get(d, 0) for d in ds) if any(d in fees for d in ds) else None
        rv = sum(rev.get(d, 0) for d in ds) if any(d in rev for d in ds) else None
        note = []
        if ds[-1] == E and (E + DAY).month == E.month:
            note.append(f"partial: through {E}")
        if m < clean and rv is not None:
            note.append("revenue before 2026-02-23 is treasury sweeps; not used for growth")
        monthly.append({"month": m.strftime("%Y-%m"), "days": len(ds), "volume": v, "fees": f, "revenue": rv,
                        "capture_bps": rv / v * 1e4 if rv is not None and v else None,
                        "share_of_fees": rv / f if rv is not None and f else None, "note": "; ".join(note)})

    mpts = sorted((p for p in hist if p["label"][0] != "-"), key=lambda p: p["label"])
    budget_rows = []
    for a, b in zip(mpts, mpts[1:] + [head]):
        da, db = dt.date.fromisoformat(a["label"]), (dt.date.fromisoformat(b["label"]) if b is not head else E + DAY)
        ds = [da + DAY * i for i in range((db - da).days)]
        pxs = [prices[d] for d in ds if d in prices]
        px = sum(pxs) / len(pxs)
        issued = supply(b) - supply(a)
        rv = sum(rev.get(d, 0) for d in ds if d <= E) if da >= dt.date(2025, 5, 1) else None
        cost = issued * px
        row = {"month": a["label"][:7], "partial": b is head, "supply_start": supply(a), "issued_near": issued,
               "issuance_rate": per_year(a, b, supply(a), supply(b)) / supply(a), "avg_price": px,
               "issuance_cost_usd": cost, "revenue_usd": rv, "coverage": rv / cost if rv is not None else None}
        if b is not head:  # month-end coverage, the T3 series (t90 run-rate vs that month's issuance cost)
            me = db - DAY
            if me - 89 * DAY >= min(rev):
                row["coverage_t90_month_end"] = window(rev, me, 90)[0] * 365 / (per_year(a, b, supply(a), supply(b)) * px)
        budget_rows.append(row)

    mpc_rows = []
    for p in mpts + [dict(head, label=f"head {E + DAY}")]:
        mm = mpc(p["mpc_state"]) or {}
        t = p.get("tee_accounts")
        mpc_rows.append({"date": p["label"][:10] if p["label"][0] != "h" else (E + DAY).isoformat(), "block": p["height"],
                         "threshold": mm.get("threshold"), "participants": mm.get("participants"),
                         "margin": mm["participants"] - mm["threshold"] if mm.get("threshold") else None,
                         "tee_entries": len(t) if t is not None else None, "version": p.get("mpc_version"),
                         "buyback_near": bb(p)})
    path, last = [], None
    for row in mpc_rows:
        k = (row["threshold"], row["participants"])
        if k != last:
            path.append(f"{k[0]}-of-{k[1]} ({row['date'][:7]})")
            last = k
    m180 = mpc(P["-180d"]["mpc_state"])
    m30 = mpc(P["-30d"]["mpc_state"])

    # ---------- snapshots (one row per raw dir) ----------
    hist_rows = []
    for d in raw_dirs:
        h = load(d + "head.json")
        hm = mpc(h["mpc_state"]) or {}
        st = sum(int(v["stake"]) for v in h["validators"]["current"]) / YOCTO
        sp = load(d + "price.json")["spot_usd"] if os.path.exists(d + "price.json") else ""
        hist_rows.append({"date": os.path.basename(d.rstrip("/\\")), "height": h["height"], "total_supply": r(supply(h), 3),
                          "validators": len(h["validators"]["current"]), "staked_pct": r(st / supply(h)),
                          "mpc_threshold": hm.get("threshold"), "mpc_participants": hm.get("participants"),
                          "tee_entries": len(h["tee_accounts"] or []), "buyback_near": r(bb(h), 3), "price_usd": sp})

    # ---------- tripwires ----------
    T = {t["id"]: t for t in cfg["tripwires"]}
    hit = lambda cond, x: x is not None and OPS[cond["op"]](x, cond["value"])
    qends = [q for y in range(2025, E.year + 1) for q in (dt.date(y, 3, 31), dt.date(y, 6, 30), dt.date(y, 9, 30), dt.date(y, 12, 31)) if q <= E]

    def last_n(values, n, cond):
        tail = values[-n:]
        return len(tail) == n and all(hit(cond, v) for v in tail)

    g_q = [(q, (growth_at(q) or {}).get("annualized")) for q in qends]
    y_q = [(q, vol_yoy_90(q)) for q in qends]
    cov_me = [(row["month"], row["coverage_t90_month_end"]) for row in budget_rows if "coverage_t90_month_end" in row]
    margin = M["participants"] - M["threshold"]
    mpc_losses = sum(1 for i in incidents if i["layer"] == "mpc_signing" and i["loss_usd"] > 0)
    unremedied = sum(1 for i in incidents if dt.date.fromisoformat(i["date"]) > E - 90 * DAY and i["loss_usd"] > 0 and not i["made_whole"])
    snaps_ramp = [x["staked_pct"] for x in hist_rows if ramp_start <= dt.date.fromisoformat(x["date"]) <= full_cut]
    t1b, t1u = T["T1"]["bear"], T["T1"]["bull"]
    t2b, t2u = T["T2"]["bear"], T["T2"]["bull"]
    t5b = T["T5"]["bear"]
    qfmt = lambda vals: ", ".join(f"{q:%Y-%m-%d} " + ("n/a" if v is None else "> +10000%" if v > 100 else pct(v, 0, True)) for q, v in vals[-4:])
    trip = [
        ("T1", pct(G["annualized"], 0, True) + f"/yr (x{mult(G['ratio'])} in 6 mo)",
         last_n([v for _, v in g_q], t1b["quarters"], t1b), last_n([v for _, v in g_q], t1u["quarters"], t1u),
         f"quarter-ends: {qfmt(g_q)} (n/a = no revenue data that far back)"),
        ("T2", pct(yoy90, 1, True) + f" (month to date {pct(vol_yoy_mtd, 1, True)})",
         last_n([v for _, v in y_q], t2b["quarters"], t2b), hit(t2u, yoy90), f"quarter-ends: {qfmt(y_q)}; year-earlier windows fall in Intents' 2025 ramp-up, which inflates this"),
        ("T3", pct(coverage, 0),
         len(cov_me) >= T["T3"]["bear"]["falls_month_ends"] + 1 and all(a[1] > b[1] for a, b in zip(cov_me[-4:], cov_me[-3:])),
         hit(T["T3"]["bull"], coverage), "month-end coverage: " + ", ".join(f"{mo} {pct(c, 0)}" for mo, c in cov_me)),
        ("T4", pct(staked / S, 2), hit(T["T4"]["bear"], staked / S),
         E >= full_cut and bool(snaps_ramp) and all(x >= T["T4"]["bull"]["value"] for x in snaps_ramp),
         f"ramp {ramp_start} to {full_cut}; {len(snaps_ramp)} snapshots in ramp so far"),
        ("T5", f"{margin} ({M['threshold']}-of-{M['participants']})",
         hit(t5b, margin) or M["threshold"] < t5b["or_threshold_below"], hit(T["T5"]["bull"], margin), ""),
        ("T6", str(mpc_losses), False, False, "from data/incidents.json (layer = mpc_signing)"),
        ("T7", str(unremedied), hit(T["T7"]["bear"], unremedied), False, "from data/incidents.json"),
    ]
    trip_text = {
        "T1": (f"< {pct(t1b['value'], 0)}/yr at {t1b['quarters']} quarter-ends running", f">= {pct(t1u['value'], 0)}/yr at {t1u['quarters']} quarter-ends running"),
        "T2": (f"< {pct(t2b['value'], 0)} at {t2b['quarters']} quarter-ends running", f"> {pct(t2u['value'], 0)}"),
        "T3": (f"falls {T['T3']['bear']['falls_month_ends']} month-ends running", f">= {pct(T['T3']['bull']['value'], 0)}"),
        "T4": (f"< {pct(T['T4']['bear']['value'], 0)}", f">= {pct(T['T4']['bull']['value'], 0)} held through ramp"),
        "T5": (f"< {t5b['value']}, or threshold < {t5b['or_threshold_below']}", f">= {T['T5']['bull']['value']}"),
        "T6": ("any -> thesis VOID", "-"),
        "T7": (">= 1", "-"),
    }
    tripwires = []
    for tid, now, bear, bull, note in trip:
        void = tid == "T6" and mpc_losses >= T["T6"]["void"]["value"]
        tripwires.append({"id": tid, "watch": T[tid]["watch"], "now": now, "bear_trigger": trip_text[tid][0],
                          "bull_trigger": trip_text[tid][1], "bear": bool(bear), "bull": bool(bull), "void": void,
                          "state": "VOID" if void else "BEAR" if bear else "BULL" if bull else "neither", "note": note})
    TW = {t["id"]: t for t in tripwires}
    n_bear = sum(t["bear"] for t in tripwires)
    verdict = ("VOID" if TW["T6"]["void"] else "DON'T HOLD" if n_bear >= 2
               else "HOLD" if TW["T1"]["bull"] and TW["T3"]["bull"] and n_bear == 0 else "ON TRACK, UNPROVEN")

    # ---------- predictions ----------
    pred_vals = {"revenue_per_day_t90": t90_rev, "vol_yoy_90d": yoy90, "mpc_threshold": M["threshold"],
                 "mpc_participants": M["participants"], "staked_pct": staked / S}
    predictions = []
    for p in cfg["predictions"]:
        ok = hit(p, pred_vals[p["metric"]])
        state = ("pass" if ok else "fail") if E >= dt.date.fromisoformat(p["by"]) else ("pending, on course" if ok else "pending, behind")
        predictions.append({**p, "now": r(pred_vals[p["metric"]]), "state": state})

    # ---------- pre-registration ----------
    reg = git("log", "--diff-filter=A", "--format=%H", "--", "config/tripwires.json").splitlines()
    edits = git("log", "--format=%H", "--", "config/tripwires.json").splitlines()
    reg_commit = reg[-1] if reg else "not committed"
    reg_note = "unchanged since" if len(edits) <= 1 else f"WARNING: edited {len(edits) - 1} time(s) after"

    # ---------- hurdle path (anchored at the first snapshot, so it stays fixed) ----------
    hurdle = C["growth_hurdle_per_year"]
    anchor_date = dt.date.fromisoformat(os.path.basename(raw_dirs[0].rstrip("/\\"))) - DAY
    anchor = window(rev, anchor_date, 90)[0] * 365
    path_pts, m = [], anchor_date.replace(day=1)
    for m in months(anchor_date.replace(day=1), full_cut):
        t = (m - anchor_date).days / 365
        path_pts.append({"month": m.strftime("%Y-%m"), "required_at_hurdle": r(anchor * (1 + hurdle) ** max(t, 0), 0),
                         "required_live": r(run_rate * (1 + required_cagr) ** max((m - E).days / 365, 0), 0)})
    actual = [{"month": row["month"], "annualized": r(row["revenue"] * 365 / row["days"], 0)}
              for row in monthly if row["revenue"]]

    # ---------- formatted values for THESIS.md ----------
    V = {
        "vol_start": min(vol).isoformat(), "fees_start": min(fees).isoformat(), "fee_switch": C["fee_switch_date"],
        "rev_material": next(x["month"] for x in monthly if x["revenue"] and x["revenue"] >= 100_000),
        "asof": (E + DAY).isoformat(), "llama_end": E.isoformat(), "height": num(head["height"]), "price": f"{price:.2f}",
        "verdict": verdict, "verdict_lower": verdict.lower(),
        "fees_annual": usd(fees30 * 365 / 30), "fees_vs_target": pct(fees30 * 365 / 30 / budget_target, 0),
        "required_cagr": pct(required_cagr, 0), "hurdle": pct(hurdle, 0), "full_cut": full_cut.strftime("%Y-%m-%d"),
        "growth": mult(G["ratio"]), "growth_ann": pct(G["annualized"], 0, True),
        "growth_vs_hurdle": "far faster than that" if G["annualized"] >= hurdle else "slower than that",
        "cap_share": pct(math.log(G["cap_ratio"]) / math.log(G["ratio"]), 0),
        "vol_yoy_mtd": pct(vol_yoy_mtd, 1, True), "vol_yoy_90": pct(yoy90, 1, True),
        "coverage": pct(coverage, 0), "run_rate": usd(run_rate), "budget": usd(budget), "budget_target": usd(budget_target),
        "gap_target": f"{budget_target / run_rate:.1f}",
        "m180_mpc": f"{m180['threshold']}-of-{m180['participants']}", "mpc_now": f"{M['threshold']}-of-{M['participants']}",
        "t1_pass": "**Yes**, but see the decomposition below" if G["annualized"] >= hurdle else "**No**",
        "t3_pass": "Yes" if coverage >= 1 else f"No, {budget_target / run_rate:.1f}x gap at {pct(C['target_issuance'])} issuance",
        "trust_pass": "**Yes**" if not mpc_losses and margin >= t5b["value"] else "**No**",
        "mpc_losses": "no signing-layer loss" if not mpc_losses else f"{mpc_losses} signing-layer loss(es)",
        "mtd_range": f"{mtd[0]:%b} {mtd[0].day}-{mtd[-1].day}", "mtd_now": usd(mtd_now), "mtd_prev": usd(mtd_prev),
        "d30_vol": pct(vol30 / vol30p - 1, 1, True), "d30_fees": pct(fees30 / fees30p - 1, 1, True), "d30_rev": pct(rev30 / rev30p - 1, 1, True),
        "fee_bps": f"{fees30 / vol30 * 1e4:.1f}", "share30": pct(rev30 / fees30),
        "bb_180": num(bb(P["-180d"])), "bb_now": num(bb(head)), "iss31_pct": pct(iss31 / S, 2),
        "yield_now": pct(iss31 / staked, 1), "yield_target": pct(C["target_issuance"] * S / staked, 1),
        "threshold": M["threshold"], "participants": M["participants"], "domains": M["domains"],
        "p30": m30["participants"], "capture": bps(capture), "be_vol": usd(be_vol), "be_mult": f"{be_vol / t90_vol:.1f}",
        "t90_vol": usd(t90_vol), "vol_x_6": f"{vol_x_at_6bps:.1f}", "months_left": f"{months_left:.0f}",
        "tvl": usd(llama["tvl_usd"]), "mpc_version": head["mpc_version"],
        "reg_commit": reg_commit, "reg_short": reg_commit[:7], "reg_note": reg_note,
        "prior_start": (G["end"] - 180 * DAY - (G["prior_days"] - 1) * DAY).isoformat(), "prior_end": (G["end"] - 180 * DAY).isoformat(),
    }

    tee_unique = len({t["account_id"] for t in tee})
    claims = [
        ("P1.1", "Intents volume, last 30 d", "D", f"**{usd(vol30)}** ({usd(vol365)} over 12 months)", "`api.llama.fi/summary/dexs/near-intents`"),
        ("P1.2", "Gross fees users paid, last 30 d", "D", f"**{usd(fees30)}** = {V['fee_bps']} bps of volume = **{V['fees_annual']}/yr**", "`summary/fees/near-intents?dataType=dailyFees`"),
        ("P1.3", f"Gross fees vs security budget at {pct(C['target_issuance'])} issuance ({usd(budget_target)}/yr)", "arith", f"**{V['fees_vs_target']}**", "P1.2 / (1.6% x supply x price)"),
        ("P1.4", "NEAR's captured share of fees, last 30 d", "D", f"**{V['share30']}** ({usd(rev30)} of {usd(fees30)})", "`dataType=dailyRevenue`"),
        ("P2.1", f"Revenue per day, trailing 90 d vs the 90 d ending 180 d earlier ({V['prior_start']} to {V['prior_end']}" + ("; includes days before the 2026-02-23 fee switch" if V["prior_start"] < C["fee_switch_date"] else "") + ")", "D+arith",
         f"{usd(G['rev'])} vs {usd(G['rev_prior'])} = **x{V['growth']}** ({V['growth_ann']}/yr annualized)", "`build.py` `growth_at()`"),
        ("P2.2", "Of which: volume", "D+arith", f"x{mult(G['vol_ratio'])} ({usd(G['vol'])} vs {usd(G['vol_prior'])} a day)", "same windows"),
        ("P2.3", "Of which: capture rate", "D+arith", f"x{mult(G['cap_ratio'])} ({bps(G['cap'])} vs {bps(G['cap_prior'])} bps); {V['cap_share']} of the growth in log terms", "revenue / volume"),
        ("P2.4", "Fee switch to buybacks live since 2026-02-23", "D", "DefiLlama methodology; [revenue.near.org](https://revenue.near.org/)", "`methodology` field"),
        ("P2.5", "Capture rate trend confirmed independently", "S", "[Nansen Q2 2026](https://nansen.ai/post/nansen-near-quarterly-report-q2-2026): 11.5% lifetime to 30.5% trailing 30 d", "-"),
        ("P2.6", "Buyback wallet balance (lower bound on purchases)", "M", f"{num(bb(head))} NEAR now, {num(bb(P['-30d']))} at -30 d; +{num(d_bb31)} over 31 d = {pct(d_bb31 / d_supply31, 0)} of net issuance in the same period", "`view_account buybacks.multisignature.near`"),
        ("P3.1", "Max issuance today", "M", f"{mi[0]}/{mi[1]} = {pct(mi[0] / mi[1])}/yr; treasury share {tr[0]}/{tr[1]} (all to stakers; some docs say 90/10, the chain says otherwise)", "`EXPERIMENTAL_protocol_config`"),
        ("P3.2", "Realized net supply growth", "M", f"{V['iss31_pct']}/yr (31 d), {pct(iss384 / S, 2)}/yr (384 d)", f"`total_supply` at blocks {P['-31d']['height']}, {P['-384d']['height']}, {head['height']}"),
        ("P3.3", "Security budget", "M+arith", f"{num(iss31)} NEAR/yr x ${V['price']} = **{usd(budget)}/yr**", "P3.2 x price"),
        ("P3.4", "Issuance path", "S", "5% to 2.5% (Oct 2025) to **1.6%** passed Nov 2 2026, phased over 24 months after a 90-day grace period", "[The Block](https://www.theblock.co/news/defi/2026-11-03-near-governance-approves-token-issuance-432378)"),
        ("P3.5", "Effect on the gap", "arith", f"break-even revenue falls from **{usd(budget)} to {usd(budget_target)}/yr** with no growth at all", "P3.3 vs P1.3"),
        ("P4.1", "MPC threshold history (month starts)", "M", " to ".join(path), "archival `v1.signer.state`"),
        ("P4.2", "No admin key on the signing contract", "M", f"{len(head['signer_access_keys'])} access keys; pending code-update votes `{json.dumps(head['contract_update_votes'])}`; code hash `{head['signer_account']['code_hash']}` (not matched to a release build); code changes need threshold votes per `near/mpc` source", "`view_access_key_list`; `contract_update_votes`"),
        ("P4.3", "TEE attestation entries", "M", f"{len(tee)} entries / {tee_unique} accounts for {M['participants']} participants (quotes not verified)", "`get_tee_accounts`"),
        ("P4.4", "External review", "S", "Five Trail of Bits audits since Mar 2025, two with high-severity findings (CKD, Robust ECDSA)", "[Trail of Bits library](https://trailofbits.com/library/near-one-mpc-chain-signatures/)"),
        ("P4.5", "Base chain", "M", f"{len(stakes)} validators; {pct(staked / S, 2)} of supply staked; {nakamoto} pools hold > 1/3 of stake", "RPC `validators`"),
        ("P4.6", "Incidents in 2026, both outside the signing layer", "S", "; ".join(f"{i['date']} {i['product']}: {i['summary']} ([source]({i['source']}))" for i in incidents), "`data/incidents.json`"),
    ]
    claim_rows = lambda pre: table(["#", "Claim", "Status", "Value", "Reproduce"], [c for c in claims if c[0].startswith(pre)])
    for p in ("P1", "P2", "P3", "P4"):
        V["claims_" + p] = claim_rows(p + ".")
    V["monthly_table"] = table(["Month", "Days", "Volume", "Gross fees", "NEAR revenue", "Capture (bps)", "Share of fees", "Note"],
                               [[x["month"], x["days"], usd(x["volume"]), usd(x["fees"]), usd(x["revenue"]),
                                 bps(x["capture_bps"] / 1e4) if x["capture_bps"] is not None else "n/a", pct(x["share_of_fees"], 0), x["note"]] for x in monthly])
    V["budget_table"] = table(["Month", "Supply at start", "NEAR issued", "Rate/yr", "Avg price", "Issuance cost", "NEAR revenue", "Revenue / cost"],
                              [[x["month"] + (" (partial)" if x["partial"] else ""), num(x["supply_start"]), num(x["issued_near"]), pct(x["issuance_rate"], 2),
                                f"${x['avg_price']:.2f}", usd(x["issuance_cost_usd"]), usd(x["revenue_usd"]), pct(x["coverage"], 0)] for x in budget_rows])
    V["mpc_table"] = table(["Date", "Block", "Threshold", "Participants", "Margin", "TEE entries", "Version", "Buyback wallet (NEAR)"],
                           [[x["date"], num(x["block"]), x["threshold"], x["participants"], x["margin"], x["tee_entries"] if x["tee_entries"] is not None else "n/a",
                             x["version"], num(x["buyback_near"]) if x["buyback_near"] is not None else "n/a"] for x in mpc_rows])
    V["tripwire_table"] = table(["ID", "Watch", "Now", "Bear trigger", "Bull trigger", "State", "Detail"],
                                [[t["id"], t["watch"], t["now"], t["bear_trigger"], t["bull_trigger"], f"**{t['state']}**", t["note"]] for t in tripwires])
    V["prediction_table"] = table(["By", "Prediction", "Now", "State"],
                                  [[p["by"], p["text"], (usd(p["now"]) + "/day" if p["metric"] == "revenue_per_day_t90" else pct(p["now"], 2) if "pct" in p["metric"] else pct(p["now"], 1, True) if "yoy" in p["metric"] else p["now"]), p["state"]] for p in predictions])

    with open("THESIS.template.md", encoding="utf-8") as f:
        write("THESIS.md", f.read().format_map(V))

    # ---------- machine outputs ----------
    out = {
        "asof": V["asof"], "defillama_through": E.isoformat(), "block": head["height"], "raw_dir": raw.replace("\\", "/"),
        "verdict": verdict,
        "preregistration": {"commit": reg_commit, "status": reg_note},
        "metrics": {k: r(v) for k, v in {
            "total_supply": S, "price_usd": price, "validators": len(stakes), "staked_pct": staked / S, "nakamoto_33": nakamoto,
            "max_inflation_rate": mi[0] / mi[1], "treasury_share": tr[0] / tr[1],
            "mpc_threshold": M["threshold"], "mpc_participants": M["participants"], "mpc_margin": margin, "mpc_domains": M["domains"],
            "tee_entries": len(tee), "tee_accounts_unique": tee_unique, "signer_access_keys": len(head["signer_access_keys"]),
            "issuance_net_per_year_31d": iss31, "issuance_net_per_year_384d": iss384, "issuance_rate_31d": iss31 / S,
            "security_budget_usd": budget, "security_budget_target_usd": budget_target,
            "buyback_near": bb(head), "buyback_delta_31d": d_bb31, "coverage_buyback": d_bb31 / d_supply31,
            "volume_30d": vol30, "fees_30d": fees30, "revenue_30d": rev30, "volume_365d": vol365,
            "revenue_per_day_t90": t90_rev, "volume_per_day_t90": t90_vol, "capture_bps_t90": capture * 1e4,
            "growth_6m": G["ratio"], "rev_growth_annualized": G["annualized"], "growth_vol_ratio": G["vol_ratio"], "growth_capture_ratio": G["cap_ratio"],
            "revenue_run_rate": run_rate, "coverage_usd": coverage, "breakeven_vol_per_day": be_vol,
            "vol_yoy_mtd": vol_yoy_mtd, "vol_yoy_90d": yoy90, "required_cagr": required_cagr, "months_to_full_cut": months_left,
            "intents_tvl_usd": llama["tvl_usd"]}.items()},
        "tripwires": tripwires, "predictions": predictions,
        "claims": [dict(zip(("id", "claim", "status", "value", "source"), c)) for c in claims],
        "daily_91d": [{"date": (E - DAY * i).isoformat(), "volume": r(vol.get(E - DAY * i), 0), "fees": r(fees.get(E - DAY * i), 0),
                       "revenue": r(rev.get(E - DAY * i), 0)} for i in range(90, -1, -1)],
        "monthly": [{k: r(v) if isinstance(v, float) else v for k, v in x.items()} for x in monthly],
        "budget_monthly": [{k: r(v) if isinstance(v, float) else v for k, v in x.items()} for x in budget_rows],
        "mpc_history": [{k: r(v) if isinstance(v, float) else v for k, v in x.items()} for x in mpc_rows],
        "hurdle": {"anchor_date": anchor_date.isoformat(), "anchor_run_rate": r(anchor, 0), "target": r(budget_target, 0),
                   "hurdle_per_year": hurdle, "path": path_pts, "actual": actual,
                   "run_rate_now": r(run_rate, 0)},
    }
    js = json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False)
    write("data/metrics.json", js + "\n")
    write("site/metrics.json", js + "\n")
    write("site/metrics.js", "window.METRICS = " + js + ";\n")
    with open("data/history.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hist_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(hist_rows)

    print(f"VERDICT: {verdict}   (data as of {V['asof']}, block {V['height']}, DefiLlama through {E})")
    for t in tripwires:
        print(f"  {t['id']} {t['state']:8} now {t['now']}")
    m = out["metrics"]
    print(f"  supply {num(S)} NEAR | staked {pct(m['staked_pct'], 2)} | nakamoto {nakamoto} | MPC {V['mpc_now']}, TEE {len(tee)}, {head['mpc_version']}")
    print(f"  issuance {num(iss31)} NEAR/yr ({V['iss31_pct']}) -> budget {usd(budget)} | run-rate {usd(run_rate)} | coverage {V['coverage']}")
    print(f"  growth x{V['growth']} ({V['growth_ann']}/yr) | capture {bps(capture)} bps | vol YoY 90d {V['vol_yoy_90']}, MTD {V['vol_yoy_mtd']}")
    print(f"  break-even {V['be_vol']}/day ({V['be_mult']}x) | required {V['required_cagr']}/yr to {full_cut}")
    print("wrote THESIS.md, data/metrics.json, data/history.csv, site/metrics.json, site/metrics.js")


if __name__ == "__main__":
    main()
