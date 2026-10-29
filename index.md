---
title: shell-bench-research — results
description: Which shell should run an agent's commands? Measured, not guessed. Cold startup, builtin loop, external spawn and RSS for ten shells on linux-cachyos.
---

# shell-bench-research

Which shell should run an agent's commands? Measured, not guessed.

Full method + corpus in the [repo](https://github.com/7not-nico/shell-bench-research).
linux-cachyos 7.3.0, x86_64, 2026-10-29. Reps: startup 20x `-c exit`; loop 5x 20k iters; spawn 5x 200x `/bin/true`. RSS via live psutil sampling.

## Cold startup, median

| shell | median | procs |
|---|---|---|
| dash 0.5.13 | 0.7 ms | 1 |
| ksh 2020 | 1.0 ms | 1 |
| bash 5.x | 1.1 ms | 1 |
| zsh 5.9.2 | 1.1 ms | 1 |
| brush 0.4.0 | 1.5 ms | 2 |
| elvish 0.21 | 3.0 ms | 1 |
| nu 0.116 | 9.0 ms | 2 |
| fish 4.9.3 | 18.7 ms | 2 |
| tcsh 6.24 | 108 ms | 2 |
| xonsh 0.25 | 262 ms | 2 |

## Builtin loop 20k / external spawn 200x / RSS, medians

| shell | loop | spawn | RSS |
|---|---|---|---|
| dash | 0.025 s | 0.084 s | 2692 KiB |
| bash | 0.044 s | 0.100 s | 2724 KiB |
| zsh | 0.038 s | 0.103 s | 2720 KiB |
| ksh | 0.039 s | 0.128 s | 4452 KiB |
| brush | 0.233 s | 0.160 s | 7044 KiB |
| elvish | 0.518 s | 0.094 s | 14364 KiB |
| nu | 0.022 s | 0.192 s | 30040 KiB |
| fish | 0.651 s | 0.133 s | 10200 KiB |
| tcsh | 0.109 s | 0.109 s | 4856 KiB |
| xonsh | 0.262 s | 6.47 s | 42636 KiB |

## Verdict

Only POSIX/bash-compatible shells can run the workload — fish, nu, elvish, xonsh, tcsh are out regardless of speed. Dash is fastest on every axis but fails 6/12 bashisms (`[[ ]]`, arrays, `<()`, `function kw`, `source`, `${V//pat/rep}`). Conclusion: bash stays pinned; shell overhead is ~1 ms against seconds of per-call latency either way.

Harness: shellcommon.py + shellbench.py + shellrss2.py. wait4 maxrss lies on sub-tick processes — see repo note.
EOF