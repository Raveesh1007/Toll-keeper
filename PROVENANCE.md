# Provenance of the pre-registration

> **Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire.**

**Claim:** the tripwires and verdict rule in `config/tripwires.json` were committed before any data was collected, and they have not changed since.

| Item | Value |
|---|---|
| Pre-registration commit | `d5491d7e3e585dade85c7a6d914587c8ed10d8f3` (author date 2026-11-13T19:17:51+05:30) |
| Files in that commit | `LICENSE`, `config/tripwires.json` only |
| `config/tripwires.json` sha256 at that commit | `524e5402b8aee0bdd4ef19b020dcbd125b80969650d7c54ee6def23fa61cf589` (identical at `HEAD`) |
| First commit adding anything under `data/raw/` | `e0d6912` ("first data run 2026-11-13"), a descendant of `d5491d7` |
| Earliest successful GitHub Actions run | [run 43451573954](https://github.com/Raveesh1007/Toll-keeper/actions/runs/43451573954), created **2026-11-13T15:20:11Z**, event `push`, `headSha` `9bfaa674cf622c44a53195985bf85da3ee6606b7` |
| Order check | `git merge-base --is-ancestor d5491d7 9bfaa67` succeeds; `git log d5491d7..9bfaa67` lists `e0d6912`, `b11acea`, `68b10d6`, `9bfaa67` |

**How the run data was obtained.** The run ID, `createdAt`, event, conclusion and `headSha` were read from the public GitHub REST API (`/repos/Raveesh1007/Toll-keeper/actions/runs`) on 2026-11-13 while the repository was public; `gh` was not available on the build machine. Two earlier runs exist (15:12:29Z on `b11acea`, 15:14:18Z on `68b10d6`); both failed at the GitHub Pages step, before Pages was enabled. Re-check with:

```
gh run view 43451573954 --repo Raveesh1007/Toll-keeper --json createdAt,headSha,conclusion,event,url
git merge-base --is-ancestor d5491d7 9bfaa674cf622c44a53195985bf85da3ee6606b7 && echo ok
git log --reverse --format='%h %ad %s' -- config/tripwires.json
git show d5491d7:config/tripwires.json | sha256sum
```

**Scope (WEAKNESSES #6).** Git commit dates are set by the author. A GitHub Actions run is timestamped by GitHub's servers and shows that a commit existed by that time, not when it was written. So this proves `d5491d7` existed by 2026-11-13T15:20:11Z and that every data file was added in a later commit; it does not independently prove the hour `d5491d7` was written. No mainnet transaction was used.
