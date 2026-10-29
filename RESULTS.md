# Shell benchmark results (linux-cachyos 7.3.0, x86_64, 2026-10-29)

Harness: `shellcommon.py` + `shellbench.py` + `shellrss2.py` (this repo).
Reps: startup 20x `-c exit`; loop 5x 20k iterations; spawn 5x 200×`/bin/true`.
RSS: sleep-held process sampled live via psutil (see `ru_maxrss-note.txt`
for why wait4 maxrss must not be used on sub-tick processes).

## Cold startup `-c exit` (median)

| shell | version | median | notes |
|---|---|---|---|
| dash | 0.5.13.4 | 0.7 ms | fastest; 1 process |
| ksh | 2020.0.0 | 1.0 ms | 1 process |
| bash | 5.x | 1.1 ms | 1 process (exec opt) |
| zsh | 5.9.2 | 1.1 ms | 1 process |
| brush | 0.4.0 | 1.5 ms | 2 processes |
| elvish | 0.21.0 | 3.0 ms | own language, 1 process |
| nu | 0.116.1 | 9.0 ms | own language, 2 processes |
| fish | 4.9.3 | 18.7 ms | own language, 2 processes |
| tcsh | 6.24.16 | 108 ms | C syntax |
| xonsh | 0.25.0 | 262 ms | Python shell; 32 ms per spawn |

## Builtin loop, 20000 iterations (median)

dash 0.025 s · nu 0.022 s · zsh 0.038 s · ksh 0.039 s · bash 0.044 s ·
tcsh 0.109 s · brush 0.233 s · xonsh 0.262 s · elvish 0.518 s · fish 0.651 s

## External spawn, 200x `/bin/true` (median)

dash 0.084 s · elvish 0.094 s · bash 0.100 s · zsh 0.103 s ·
tcsh 0.109 s · ksh 0.128 s · fish 0.133 s · brush 0.160 s ·
nu 0.192 s · xonsh 6.47 s (disqualified: ~32 ms per spawn)

## RSS, sleep-held (psutil)

bash 2724 KiB · dash 2692 KiB · zsh 2720 KiB · ksh 4452 KiB ·
tcsh 4856 KiB · brush 7044 KiB · fish 10200 KiB · elvish 14364 KiB ·
nu 30040 KiB · xonsh 42636 KiB

## Verdict for agent command execution (spawn-heavy, bash syntax)

Only POSIX/bash-compatible shells can run the workload at all, which
eliminates fish, nu, elvish, xonsh, tcsh regardless of speed. Of the
eligible set, dash is fastest on every axis but cannot run bashisms;
the compatibility corpus (`dash_corpus.py`, 12 constructs) scores
dash 6 PASS / 6 FAIL (`[[ ]]`, arrays, `<()`, `function kw`, `source`,
`${V//pat/rep}` all fail). Conclusion: keep `bash` pinned
(`"shell": "/bin/bash"` in opencode.json); shell overhead is ~1 ms
against seconds of per-call latency either way.
`dune` in Arch repos is the OCaml build system, not the shell — excluded.
