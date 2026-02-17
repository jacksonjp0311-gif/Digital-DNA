import json, random, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/"ecosystem/state"
STATE.mkdir(parents=True,exist_ok=True)

POP_FILE=STATE/"population.json"

POP_SIZE=4
GENERATIONS=50
STEPS=200

def write_genome(workdir):
    genome={
        "param_step_delay":random.uniform(0.01,0.08),
        "mutation_bias":random.uniform(-1,1)
    }
    (workdir/"genome.json").write_text(json.dumps(genome,indent=2))

def run_org(i,workdir):
    write_genome(workdir)

    cmd=[
        sys.executable,
        str(ROOT/"engine/evolution/evolution_loop.py"),
        "--steps",str(STEPS),
        "--workdir",str(workdir),
        "--id",str(i)
    ]

    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)

    for line in p.stdout:
        print(f"[ORG{i}] {line.strip()}")

    p.wait()

    try:
        res=json.loads((workdir/"result.json").read_text())
        return res["score"]
    except:
        return -999

def main():
    best_score=-999

    for g in range(GENERATIONS):
        print(f"[GEN] {g+1}/{GENERATIONS}")

        scores=[]

        for i in range(POP_SIZE):
            wd=STATE/f"org_{i}"
            wd.mkdir(parents=True,exist_ok=True)

            s=run_org(i,wd)
            scores.append(s)

        gen_best=max(scores)

        print(f"[SELECT] best_score={gen_best}")

        best_score=gen_best

        time.sleep(0.5)

if __name__=="__main__":
    main()
