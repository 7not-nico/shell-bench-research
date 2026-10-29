"""Shared harness for shell spawn/loop/RSS benchmarks.

One home for: binary names, per-family code snippets (with fallback
candidates for shells whose exact syntax is uncertain), timing, winner
picking, and RSS sampling. Drivers stay thin.
"""

import os
import shutil
import statistics
import subprocess
import time

BINARIES = {
    "bash": "bash", "brush": "brush", "fish": "fish", "dash": "dash",
    "ksh": "ksh", "zsh": "zsh", "tcsh": "tcsh", "xonsh": "xonsh",
    "nu": "nu", "elvish": "elvish",
}

ORDER = ["bash", "brush", "fish", "dash", "ksh", "zsh",
         "tcsh", "xonsh", "nu", "elvish"]

LOOP_ITERS = 20000
SPAWN_ITERS = 200
STARTUP_N = 20
WORK_N = 5

POSIX_LOOP = "i=0; while [ $i -lt %d ]; do i=$((i + 1)); done" % LOOP_ITERS
POSIX_SPAWN = "for i in $(seq 1 %d); do /bin/true; done" % SPAWN_ITERS
FISH_LOOP = ("set i 0; while test $i -lt %d; set i (math $i + 1); end"
             % LOOP_ITERS)
FISH_SPAWN = "for i in (seq 1 %d); /bin/true; end" % SPAWN_ITERS
TCSH_LOOP = "@ i = 0; while ($i < %d); @ i++; end" % LOOP_ITERS
TCSH_SPAWN = "foreach i (`seq 1 %d`); /bin/true; end" % SPAWN_ITERS
XONSH_LOOP = "i=0\nwhile i<%d:\n i+=1" % LOOP_ITERS
NU_LOOP = "mut x = 0; for i in 1..%d { $x += 1 }" % LOOP_ITERS
NU_SPAWN = "for i in 1..%d { ^/bin/true }" % SPAWN_ITERS
ELVISH_LOOP_A = ("var i = 0; for x [(range %d)] { set i = (+ $i 1) }"
                 % LOOP_ITERS)
ELVISH_LOOP_B = ("range %d | each {|x| /bin/true }" % LOOP_ITERS)
ELVISH_SPAWN_A = "for x [(range %d)] { /bin/true }" % SPAWN_ITERS
ELVISH_SPAWN_B = ("range %d | each {|x| /bin/true }" % SPAWN_ITERS)
XONSH_SPAWN_A = "for i in range(%d):\n /bin/true" % SPAWN_ITERS

SLEEPS = {"bash": "sleep 60", "brush": "sleep 60", "fish": "sleep 60",
          "dash": "sleep 60", "ksh": "sleep 60", "zsh": "sleep 60",
          "tcsh": "sleep 60", "xonsh": "sleep 60", "nu": "^sleep 60",
          "elvish": "sleep 60"}


def binary(name):
    """Absolute path or None when not installed."""
    return shutil.which(BINARIES[name])


def loop_candidates(name):
    if name in ("bash", "brush", "dash", "ksh", "zsh"):
        return [POSIX_LOOP]
    if name == "fish":
        return [FISH_LOOP]
    if name == "tcsh":
        return [TCSH_LOOP]
    if name == "xonsh":
        return [XONSH_LOOP]
    if name == "nu":
        return [NU_LOOP]
    if name == "elvish":
        return [ELVISH_LOOP_A, ELVISH_LOOP_B]
    raise KeyError(name)


def spawn_candidates(name):
    if name in ("bash", "brush", "dash", "ksh", "zsh"):
        return [POSIX_SPAWN]
    if name == "fish":
        return [FISH_SPAWN]
    if name == "tcsh":
        return [TCSH_SPAWN]
    if name == "xonsh":
        return [XONSH_SPAWN_A]
    if name == "nu":
        return [NU_SPAWN]
    if name == "elvish":
        return [ELVISH_SPAWN_A, ELVISH_SPAWN_B]
    raise KeyError(name)


def run_once(argv, timeout=120):
    t0 = time.perf_counter()
    p = subprocess.run(argv, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=timeout)
    dt = time.perf_counter() - t0
    return dt, p.returncode, p.stdout.decode("utf-8", "replace")[:200]


def pick_working(path, candidates):
    """First candidate with rc==0 as argv; else (None, last rc, last err)."""
    last = (None, -1, "no candidates")
    for code in candidates:
        _, rc, err = run_once([path, "-c", code])
        last = (None, rc, err)
        if rc == 0:
            return [path, "-c", code], rc, err
    return last


def bench(argv, reps):
    samples = []
    rc, err = 0, ""
    for _ in range(reps):
        dt, rc, err = run_once(argv)
        samples.append(dt)
        if rc != 0:
            break
    return min(samples), statistics.median(samples), rc, err


def rss_hold(path, code):
    """RSS of a held process + child count; terminates afterwards."""
    import psutil
    p = subprocess.Popen([path, "-c", code],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    try:
        time.sleep(0.5)
        proc = psutil.Process(p.pid)
        kids = proc.children(recursive=True)
        return proc.memory_info().rss // 1024, len(kids)
    finally:
        p.terminate()
        p.wait()
