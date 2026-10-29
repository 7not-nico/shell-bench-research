#!/usr/bin/env python3
"""dash-versus-bash compatibility corpus: 12 constructs from real agent commands."""
import subprocess
import os
import sys

TMP = "/tmp/opencode"
os.makedirs(TMP, exist_ok=True)

CONSTRUCTS = [
    ("01-cmdsubst", "echo $(echo hi)", "capture via $()"),
    ("02-arith", "echo $((2 + 3))", "arithmetic $(( ))"),
    ("03-default", "FOO=; echo ${FOO:-fallback}", "default ${VAR:-d}"),
    ("04-single-test", "[ -f /etc/hosts ] && echo exists", "POSIX [ ] + && chain"),
    ("05-double-test", "[[ -f /etc/hosts ]] && echo exists", "bash [[ ]]"),
    ("06-array", "arr=(a b c); echo ${arr[1]}", "bash array"),
    ("07-procsubst", "cat <(echo hello)", "process subst <()"),
    ("08-pipefail", "set -o pipefail; false | true; echo $?", "set -o pipefail"),
    ("09-function-kw", "function foo { echo hi; }; foo", "function kw"),
    ("10-source", f"echo 'X=42' > {TMP}/dash_corpus_src.sh; source {TMP}/dash_corpus_src.sh; echo $X", "source builtin"),
    ("11-amp-redirect", f"echo hi &> {TMP}/dash_corpus_out.txt; cat {TMP}/dash_corpus_out.txt", "bash &> redirect"),
    ("12-str-replace", "V=hello-world; echo ${V//o/0}", "bash ${V//o/0}"),
]

def run(shell, snippet):
    try:
        p = subprocess.run([shell, "-c", snippet], capture_output=True, text=True, timeout=10)
        return p.returncode, p.stdout.strip(), p.stderr.strip()[:200]
    except FileNotFoundError as e:
        return 127, "", f"no shell: {e}"[:200]
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"

def main():
    print("construct | shell | rc | stdout | verdict")
    print("---|---|---|---|---")
    passes = 0
    fails = 0
    rows = []
    for name, snippet, desc in CONSTRUCTS:
        brc, bout, berr = run("bash", snippet)
        drc, dout, derr = run("dash", snippet)
        match = (brc == drc and bout == dout)
        verdict = "PASS" if match else "FAIL"
        if match:
            passes += 1
        else:
            fails += 1
        rows.append((name, desc, brc, bout, drc, dout, verdict, berr, derr))
        # one line per construct, dash-vs-bash pair
        print(f"{name} ({desc}) | bash rc={brc} out={bout!r} || dash rc={drc} out={dout!r} | {verdict}")
    print(f"\nSUMMARY: {passes} PASS, {fails} FAIL out of {len(CONSTRUCTS)}")
    print(f"POSIX-only (01-04): {[r[6] for r in rows[:4]]}")
    print(f"bashisms (05-12): {[r[6] for r in rows[4:]]}")
    if fails == 0:
        print("VERDICT: dash ADOPTABLE for full scope")
    elif all(r[6] == "PASS" for r in rows[:4]) and all(r[6] == "FAIL" for r in rows[4:]):
        print("VERDICT: dash SAFE for POSIX-only trial scope (01-04); UNSAFE for full agent-command scope (05-12 bashisms fail) — trial must forbid [[ ]], arrays, <(), pipefail, function-kw, source, &>, ${//}")
    else:
        print("VERDICT: dash PARTIAL — see table; trial scope must exclude FAIL constructs")
    return 0

if __name__ == "__main__":
    sys.exit(main())
