"""Smallest check that fails if the core arithmetic in build.py breaks. Run: python test_build.py"""
import datetime as dt
from build import mpc, pct, usd, window

d = dt.date(2026, 3, 10)
s = {d - dt.timedelta(i): float(i) for i in range(20)}           # 0,1,2,... going back in time
assert window(s, d, 10) == (4.5, 10)                              # mean of 0..9
assert window(s, d, 10, start=d - dt.timedelta(3)) == (1.5, 4)    # clipped to 4 days: mean of 0..3
assert window(s, d, 30)[0] == sum(range(20)) / 30                 # missing days count as 0
assert usd(3.774e9) == "$3.77B" and usd(57_700) == "$57.7k" and usd(999_999) == "$1M" and usd(18) == "$18"
assert pct(0.0359, 1, True) == "+3.6%"
st = {"Running": {"parameters": {"threshold": 11, "participants": {"participants": [["a.near", 0, {}], ["b.near", 1, {}]]}},
                  "domains": {"domains": [{}, {}, {}]}}}
assert mpc(st) == {"kind": "Running", "threshold": 11, "participants": 2, "ids": ["a.near", "b.near"], "domains": 3}
import shutil, subprocess
if shutil.which("node"):  # JS slider model must agree with build.py on today's defaults
    r = subprocess.run(["node", "test_model.js"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
else:
    print("node not found: JS/Python model agreement check (test_model.js) skipped")
print("ok")
