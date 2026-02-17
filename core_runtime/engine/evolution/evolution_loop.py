import time, json, random, os
from pathlib import Path

def _load_genome():
    try:
        return json.loads(Path("genome.json").read_text())
    except:
        return {"param_step_delay":0.01,"mutation_bias":0}

GENOME=_load_genome()
STEP_DELAY=max(0.001,float(GENOME.get("param_step_delay",0.01)))
BIAS=float(GENOME.get("mutation_bias",0))

def _write_result(workdir,payload):
    wd=Path(workdir) if workdir else Path(".")
    wd.mkdir(parents=True,exist_ok=True)
    payload["ts"]=time.time()
    (wd/"result.json").write_text(json.dumps(payload,indent=2))

if __name__=="__main__":
    import argparse

    parser=argparse.ArgumentParser()
    parser.add_argument("--steps",type=int,default=0)
    parser.add_argument("--workdir",type=str,default=None)
    parser.add_argument("--id",type=int,default=-1)
    args=parser.parse_args()

    if args.workdir:
        Path(args.workdir).mkdir(parents=True,exist_ok=True)
        os.chdir(args.workdir)

    print("[LOOP] starting")

    for i in range(args.steps):
        print(f"[LOOP] step {i+1}/{args.steps}")
        time.sleep(STEP_DELAY)

    # FITNESS SIGNAL
    score=float(args.steps)+(BIAS*10)+random.uniform(-5,5)

    _write_result(args.workdir or ".",{
        "organism_id":args.id,
        "steps":args.steps,
        "score":score
    })

    print("[LOOP] wrote result.json")

