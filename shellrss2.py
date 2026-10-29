"""Thin driver: per-shell RSS via live psutil sampling (cross-checks wait4)."""
import sys

sys.path.insert(0, "/tmp/opencode")

import shellcommon as sc

for name in sc.ORDER:
    path = sc.binary(name)
    if path is None:
        print("%-8s not installed" % name)
        continue
    rss_kb, kids = sc.rss_hold(path, sc.SLEEPS[name])
    print("%-8s rss=%dKiB children=%d" % (name, rss_kb, kids))
