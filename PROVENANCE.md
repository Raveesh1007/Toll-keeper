# Provenance: were the alarms written before the data?

> **Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire.**

**Yes.** The tripwires and verdict rule (`config/tripwires.json`) were committed before any data was collected, and they have not been edited since.

| Evidence | Value |
|---|---|
| Pre-registration commit | `d5491d7` (`d5491d7e3e585dade85c7a6d914587c8ed10d8f3`), the first commit in the repo. It contains only `LICENSE` and `config/tripwires.json`. |
| Alarm file fingerprint | sha256 `524e5402b8aee0bdd4ef19b020dcbd125b80969650d7c54ee6def23fa61cf589`, identical today |
| First data | Added in a later commit, `e0d6912` |
| Independent timestamp | [GitHub Actions run 43451573954](https://github.com/Raveesh1007/Toll-keeper/actions/runs/43451573954), timestamped by GitHub at **2026-11-13 15:20:11 UTC**, ran on commit `9bfaa67`, which descends from `d5491d7` |

**Check it yourself**

```
git log --reverse --format='%h %ad %s' -- config/tripwires.json    # only d5491d7
git show d5491d7:config/tripwires.json | sha256sum                  # 524e5402...
git merge-base --is-ancestor d5491d7 9bfaa67 && echo ok              # d5491d7 came first
```

Then open the run link above and confirm its time and commit.

**What this does not prove.** Git commit dates are set by the author. The GitHub run proves `d5491d7` existed by 2026-11-13 15:20:11 UTC and that all data was added after it; it does not prove the exact hour `d5491d7` was written.
