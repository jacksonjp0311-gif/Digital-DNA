# ==========================================================
# DIGITAL-DNA — PARALLEL ENTRYPOINT (NON-DESTRUCTIVE)
# Purpose: run 4 organisms in parallel without touching run.py
# ==========================================================

import os, sys, subprocess
import multiprocessing as mp
from pathlib import Path

POP_SIZE = int(os.environ.get("DDNA_POP", "4"))
STEPS    = int(os.environ.get("DDNA_STEPS", "200"))

BASE = Path("ecosystem/runtime")
BASE.mkdir(parents=True, exist_ok=True)

def _pump(prefix: str, pipe):
    # Prefix every output line so parallel logs stay readable.
    for line in iter(pipe.readline, ""):
        if not line:
            break
        line = line.rstrip("\n")
        if line:
            print(f"{prefix} {line}", flush=True)

def run_org(i: int):
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
        text=True,
        bufsize=1,
        cwd=str(Path.cwd())
    )
    _pump(f"[ORG{i}]", p.stdout)
    return p.wait()

def main():
    print(f"[PARALLEL] POP_SIZE={POP_SIZE} STEPS={STEPS}", flush=True)
    procs = []
    for i in range(POP_SIZE):
        p = mp.Process(target=run_org, args=(i,))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()

if __name__ == "__main__":
    mp.freeze_support()
    main()
