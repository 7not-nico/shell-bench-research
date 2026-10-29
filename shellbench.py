"""Thin driver: bench all shells via shellcommon (startup/loop/spawn)."""
import sys

sys.path.insert(0, "/tmp/opencode")

import shellcommon as sc

REPS = {"startup": sc.STARTUP_N, "loop": sc.WORK_N, "spawn": sc.WORK_N}

CASES = {}
for name in sc.ORDER:
    path = sc.binary(name)
    if path is None:
        continue
    CASES.setdefault("startup", {})[name] = [path, "-c", "exit"]
    loop_argv, rc, err = sc.pick_working(path, sc.loop_candidates(name))
    CASES.setdefault("loop", {})[name] = loop_argv or [path, "-c", "exit"]
    if loop_argv is None:
        print("note: %s loop syntax failed rc=%d err=%r" % (name, rc, err))
    spawn_argv, rc, err = sc.pick_working(path, sc.spawn_candidates(name))
    CASES.setdefault("spawn", {})[name] = spawn_argv or [path, "-c", "exit"]
    if spawn_argv is None:
        print("note: %s spawn syntax failed rc=%d err=%r" % (name, rc, err))

for case in ("startup", "loop", "spawn"):
    print("== %s ==" % case)
    for name, argv in CASES.get(case, {}).items():
        lo, med, rc, err = sc.bench(argv, REPS[case])
        line = "  %-8s min=%.4fs median=%.4fs rc=%d" % (name, lo, med, rc)
        if rc != 0:
            line += " err=%r" % err
        print(line)
