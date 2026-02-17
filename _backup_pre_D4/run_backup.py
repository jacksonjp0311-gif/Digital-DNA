import subprocess, sys, time, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run_single():
    while True:
        p = subprocess.Popen(
            [sys.executable, "engine/evolution/evolution_loop.py"],
            cwd=ROOT
        )
        p.wait()
        time.sleep(0.5)

def run_population():
    while True:
        procs = []
        for i in range(4):
            procs.append(
                subprocess.Popen(
                    [sys.executable, "engine/evolution/evolution_loop.py"],
                    cwd=ROOT
                )
            )

        for p in procs:
            p.wait()

        print("GENERATION COMPLETE")

mode = "single"
if len(sys.argv) > 1:
    mode = sys.argv[1]

if mode == "population":
    run_population()
else:
    run_single()
