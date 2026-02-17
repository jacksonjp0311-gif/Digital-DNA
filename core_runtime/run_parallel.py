import subprocess
import sys
import os
from pathlib import Path

POP_SIZE = 4
STEPS = 200

BASE = Path("ecosystem/runtime")
BASE.mkdir(parents=True, exist_ok=True)

procs = []

print(f"[PARALLEL] starting POP={POP_SIZE}", flush=True)

for i in range(POP_SIZE):
    wd = BASE / f"org_{i}"
    wd.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "engine/evolution/evolution_loop.py",
        "--steps", str(STEPS),
        "--workdir", str(wd),
        "--id", str(i)
    ]

    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    procs.append((i,p))

# non-blocking read
while procs:
    for item in list(procs):
        i,p = item
        line = p.stdout.readline()

        if line:
            print(f"[ORG{i}] {line.rstrip()}", flush=True)

        if p.poll() is not None:
            # flush remaining
            for l in p.stdout.readlines():
                print(f"[ORG{i}] {l.rstrip()}", flush=True)
            procs.remove(item)

print("[PARALLEL COMPLETE]", flush=True)
