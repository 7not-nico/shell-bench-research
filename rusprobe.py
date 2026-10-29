"""Root-cause probe: wait4 ru_maxrss vs live psutil RSS across shells."""
import os
import shutil
import subprocess
import time

import psutil


def wait4_probe(path, code="exit", reps=3):
    out = []
    for _ in range(reps):
        p = subprocess.Popen([path, "-c", code],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        _, _, ru = os.wait4(p.pid, 0)
        out.append((ru.ru_maxrss, ru.ru_minflt, ru.ru_majflt))
    return out


def held_rss(path, code="sleep 30"):
    p = subprocess.Popen([path, "-c", code],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    try:
        time.sleep(0.3)
        return psutil.Process(p.pid).memory_info().rss // 1024
    finally:
        p.terminate()
        p.wait()


for name in ("bash", "brush", "dash", "fish"):
    path = shutil.which(name)
    if not path:
        print("%-6s missing" % name)
        continue
    print(name, "wait4:", wait4_probe(path), "held_rss_KiB:", held_rss(path))
