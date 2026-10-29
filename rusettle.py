"""Settle wait4 semantics: per-child max or cumulative max over reaped children?"""
import os
import subprocess


def reap(argv):
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    _, _, ru = os.wait4(p.pid, 0)
    return ru.ru_maxrss


big = reap(["python3", "-c", "a = bytearray(60 * 1024 * 1024)"])
small_after_big = reap(["dash", "-c", "exit"])
small_alone_first = reap(["dash", "-c", "exit"])
print("big_python_60MB:", big)
print("dash_after_big :", small_after_big)
print("dash_again     :", small_alone_first)
print("cumulative?" , small_after_big >= big)
