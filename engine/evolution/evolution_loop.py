def compute_fitness(result):
    score = result.get("score",0)
    steps = result.get("steps",0)

    runtime_penalty = 0
    crash_penalty = 0
    stability_bonus = 5

    return score + stability_bonus - runtime_penalty - crash_penalty
def ensure_genome(workdir, gid):
    import json, random
    from pathlib import Path
    gfile = Path(workdir) / "genome.json"

    if not gfile.exists():
        genome = {
            "param_step_delay": random.uniform(0.02,0.08),
            "param_noise": random.uniform(0.01,0.05),
            "code_mutation_rate": 0.05,
            "generation": gid
        }
        gfile.write_text(json.dumps(genome,indent=2))
        return genome

    return json.loads(gfile.read_text())
import os, sys, time, json, random
from pathlib import Path

def _write_result(workdir, payload):
    wd = Path(workdir) if workdir else Path(".")
    wd.mkdir(parents=True, exist_ok=True)
    payload["ts"] = time.time()
    (wd / "result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

def _selftest(workdir=None):
    print("[SELFTEST] probing loop...")
    # minimal filesystem check
    try:
        _write_result(workdir or ".", {"organism_id": -1, "score": 1.0, "steps": 1, "selftest": True})
    except Exception as e:
        print("[SELFTEST] False")
        print("[SELFTEST] error:", e)
        return 1
    print("[SELFTEST] True")
    return 0

def main(argv=None):
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=0)
    p.add_argument("--workdir", type=str, default=None)
    p.add_argument("--id", type=int, default=-1)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)

    if args.workdir:
        wd = Path(args.workdir)
        wd.mkdir(parents=True, exist_ok=True)
        os.chdir(wd)

    if args.selftest:
        return _selftest(args.workdir)

    print("[LOOP] starting")

    # Infinite loop mode (for D)
    if args.steps <= 0:
        i = 0
        while True:
            i += 1
            print(f"[LOOP] iter {i}")
            time.sleep(1.0)
        # unreachable

    # Finite steps mode (A/B/C)
    for i in range(args.steps):
        print(f"[LOOP] step {i+1}/{args.steps}")
        time.sleep(0.01)

    # Score model (placeholder): stable + tiny id jitter so selection can work deterministically
    score = float(args.steps) + (args.id * 0.001)

    try:
        _write_result(args.workdir or ".", {"organism_id": args.id, "score": score, "steps": args.steps})
        print("[LOOP] wrote result.json")
    except Exception as e:
        print("[LOOP] result write failed:", e)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
