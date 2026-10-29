# shell-bench-research

Which shell should run an agent's commands? Measured, not guessed.

## Contents

- `shellcommon.py` — shared harness: per-family snippets (with fallback
  candidates for uncertain syntax), timing, winner-picking, RSS sampling
- `shellbench.py` — thin driver: cold startup, builtin loop, external spawn
- `shellrss2.py` — thin driver: per-shell RSS via live psutil sampling
- `rusprobe.py`, `rusettle.py` — wait4 maxrss anomaly probes
- `RESULTS.md` — full numbers (10 shells, linux-cachyos 7.3.0, 2026-10-29)
- `dash_corpus.py` — 12-construct bash-compatibility corpus (dash: 6/12)
- `ru_maxrss-note.txt` — why wait4 maxrss lies on sub-tick processes
- `history-check.txt` — sysstat/atop history verification evidence
- `psi.py` — PSI (`/proc/pressure`) snapshot helper for gauges
- `dool-smoke.csv` — sample `dool` CSV capture

## Reproduce

```bash
python3 shellbench.py   # ~2 min: startup x20, loop x5, spawn x5 per shell
python3 shellrss2.py    # RSS of sleep-held shells
python3 dash_corpus.py  # bashism compatibility table
```

Only shells installed on the box are measured; missing ones are skipped
with a note. Niche/AUR-only shells (murex, oils, ion, nsh, yash, mksh…)
are catalogued in RESULTS.md but unmeasured.

## Bottom line

For spawn-heavy bash-syntax command execution: bash wins among eligible
shells; dash is faster but fails 6/12 bashisms. Interactive shells
(fish, nushell, elvish, xonsh) can't run the workload at all.
