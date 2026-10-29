"""PSI polling helper for gauges: snapshots of /proc/pressure stalls.

Near-zero overhead: three small file reads, no daemons, no sampling
processes. psutil does not expose PSI, so gauges import this directly.
"""

import os

RESOURCES = ("cpu", "io", "memory")
BASE = "/proc/pressure"


def snapshot():
    """Return {resource.scope: {avg10, avg60, avg300, total}}."""
    out = {}
    for res in RESOURCES:
        try:
            with open(os.path.join(BASE, res)) as f:
                lines = f.read().splitlines()
        except OSError:
            continue
        for line in lines:
            parts = line.split()
            if not parts:
                continue
            scope, kvs = parts[0], parts[1:]
            vals = {}
            for kv in kvs:
                key, _, val = kv.partition("=")
                try:
                    vals[key] = float(val)
                except ValueError:
                    pass
            out["%s.%s" % (res, scope)] = vals
    return out


def oneline(snap):
    """Compact one-line rendering for gauge logs."""
    bits = []
    for key in sorted(snap):
        v = snap[key]
        bits.append(
            "%s avg10=%.2f avg60=%.2f avg300=%.2f total=%.0f"
            % (key, v.get("avg10", 0.0), v.get("avg60", 0.0),
               v.get("avg300", 0.0), v.get("total", 0.0))
        )
    return " | ".join(bits)


if __name__ == "__main__":
    print(oneline(snapshot()))
