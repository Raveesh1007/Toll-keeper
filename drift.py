"""Re-fetch DefiLlama and compare it with the committed snapshot (newest data/raw/<date>/defillama.json).
Writes data/derived/drift.json: every day whose value changed by more than 0.5%, plus whether the verdict or any
tripwire state would change if the build used the fresh series. Standard library only; touches nothing else.
Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire."""
import datetime as dt, glob, hashlib, json, os, shutil, subprocess, sys, tempfile
from collect import LLAMA, http

THRESHOLD = 0.005
SERIES = {"volume": "/summary/dexs/near-intents?excludeTotalDataChartBreakdown=true",
          "fees": "/summary/fees/near-intents?dataType=dailyFees&excludeTotalDataChartBreakdown=true",
          "revenue": "/summary/fees/near-intents?dataType=dailyRevenue&excludeTotalDataChartBreakdown=true"}


def day(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    snap_dir = sorted(glob.glob("data/raw/*/"))[-1]
    snap = json.load(open(snap_dir + "defillama.json", encoding="utf-8"))
    def chart(path):
        r = http(LLAMA + path)
        return {kk: r.get(kk) for kk in ("totalDataChart", "total24h", "total30d", "total60dto30d", "methodology")}
    fresh = {k: chart(path) for k, path in SERIES.items()}
    fresh["tvl_usd"] = snap.get("tvl_usd")  # TVL is not a daily series; keep the snapshot value
    changes, new_days = [], {}
    for k in SERIES:
        old = {day(t): v for t, v in snap[k]["totalDataChart"]}
        new = {day(t): v for t, v in fresh[k]["totalDataChart"]}
        new_days[k] = sorted(d for d in new if d not in old)
        for d in sorted(set(old) & set(new)):
            o, n = old[d], new[d]
            if o != n and (o == 0 or abs(n - o) / abs(o) > THRESHOLD):
                changes.append({"series": k, "date": d, "old": o, "new": n, "change_pct": None if o == 0 else round((n - o) / o * 100, 2)})

    # rebuild in a scratch copy with the fresh series swapped in, then compare verdict and tripwire states
    committed = json.load(open("data/metrics.json", encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        for f in ("build.py", "security.py", "THESIS.template.md", "METHODS.template.md", "WEAKNESSES.template.md", "README.md"):
            shutil.copy(f, tmp)
        shutil.copytree("config", os.path.join(tmp, "config"))
        os.makedirs(os.path.join(tmp, "data"))
        shutil.copy("data/incidents.json", os.path.join(tmp, "data"))
        shutil.copytree("data/defillama", os.path.join(tmp, "data", "defillama"))
        shutil.copytree("data/raw", os.path.join(tmp, "data", "raw"))
        with open(os.path.join(tmp, snap_dir, "defillama.json"), "w", encoding="utf-8") as f:
            json.dump(fresh, f)
        run = subprocess.run([sys.executable, "build.py"], cwd=tmp, capture_output=True, text=True, encoding="utf-8")
        rebuilt = json.load(open(os.path.join(tmp, "data", "metrics.json"), encoding="utf-8")) if run.returncode == 0 else None
    states = lambda m: {t["id"]: t["state"] for t in m["tripwires"]}
    out = {
        "label": "Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire.",
        "snapshot": snap_dir.replace("\\", "/"),
        "snapshot_defillama_sha256": hashlib.sha256(open(snap_dir + "defillama.json", "rb").read()).hexdigest(), "fetched_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "threshold_pct": THRESHOLD * 100, "revised_days": changes, "new_days_since_snapshot": new_days,
        "verdict_committed": committed["verdict"], "verdict_with_fresh_data": rebuilt["verdict"] if rebuilt else None,
        "tripwire_state_changes": [{"id": i, "committed": s, "with_fresh_data": states(rebuilt)[i]}
                                   for i, s in states(committed).items() if rebuilt and states(rebuilt)[i] != s],
        "rebuild_error": None if rebuilt else run.stderr[-500:],
    }
    os.makedirs("data/derived", exist_ok=True)
    with open("data/derived/drift.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f"drift vs {out['snapshot']}: {len(changes)} revised day(s) > {THRESHOLD * 100}%, "
          f"new days {sum(len(v) for v in new_days.values())}; verdict {out['verdict_committed']} -> {out['verdict_with_fresh_data']}; "
          f"tripwire changes: {out['tripwire_state_changes'] or 'none'}")
    for c in changes:
        print(f"  {c['series']:8} {c['date']}  {c['old']:,} -> {c['new']:,}  ({c['change_pct']}%)")
    print("wrote data/derived/drift.json")


if __name__ == "__main__":
    main()
