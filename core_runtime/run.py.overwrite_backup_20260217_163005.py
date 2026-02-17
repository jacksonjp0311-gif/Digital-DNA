# ================= PARALLEL ENTRY =================
import multiprocessing as mp
import subprocess, sys
from pathlib import Path

POP_SIZE = 4
STEPS = 200
BASE = Path("ecosystem/runtime")
BASE.mkdir(parents=True, exist_ok=True)

def run_org(i):
    wd = BASE/f"org_{i}"
    wd.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "engine/evolution/evolution_loop.py",
        "--steps", str(STEPS),
        "--workdir", str(wd),
        "--id", str(i)
    ]
    subprocess.run(cmd)

def main():
    jobs=[]
    for i in range(POP_SIZE):
        p=mp.Process(target=run_org,args=(i,))
        p.start()
        jobs.append(p)

    for j in jobs:
        j.join()

if __name__=="__main__":
    main()
# ==================================================
