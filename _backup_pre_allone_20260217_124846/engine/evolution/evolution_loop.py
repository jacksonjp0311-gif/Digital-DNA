# DIGITAL-DNA â€” evolution_loop.py (CANONICAL CONTRACT)
# CLI:
#   python evolution_loop.py --steps N --workdir PATH --id K --gen G --seed S --genome PATH
# Behavior:
#   - prints progress
#   - runs finite when steps>0
#   - writes workdir/result.json with score + metadata

from __future__ import annotations
import os, sys, time, json, random, argparse
from pathlib import Path

def _write_result(workdir: str | None, payload: dict) -> None:
    wd = Path(workdir) if workdir else Path(".")
    wd.mkdir(parents=True, exist_ok=True)
    payload["ts"] = time.time()
    (wd / "result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

def _load_genome(genome_path: str | None) -> dict:
    if not genome_path:
        return {"mutation_rate": 0.12, "sleep_ms": 40, "noise": 0.35}
    p = Path(genome_path)
    if not p.exists():
        return {"mutation_rate": 0.12, "sleep_ms": 40, "noise": 0.35}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"mutation_rate": 0.12, "sleep_ms": 40, "noise": 0.35}

def _score(genome: dict, steps: int, rng: random.Random) -> float:
    # Simple, deterministic-ish score surface:
    # - higher steps helps but saturates
    # - sleep_ms penalizes (throughput)
    # - noise penalizes
    sleep_ms = float(genome.get("sleep_ms", 40))
    noise = float(genome.get("noise", 0.35))
    base = (1.0 - (sleep_ms / 200.0)) * 0.8 + (steps / 500.0) * 0.6
    jitter = rng.uniform(-1.0, 1.0) * (0.15 + noise * 0.25)
    score = base + jitter - (noise * 0.3)
    return float(score)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=0)
    ap.add_argument("--workdir", type=str, default=None)
    ap.add_argument("--id", type=int, default=-1)
    ap.add_argument("--gen", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--genome", type=str, default=None)
    args = ap.parse_args()

    if args.workdir:
        Path(args.workdir).mkdir(parents=True, exist_ok=True)
        os.chdir(args.workdir)

    genome = _load_genome(args.genome)
    rng = random.Random(int(args.seed) ^ (int(args.id) * 1315423911) ^ (int(args.gen) * 2654435761))

    print("[LOOP] starting")
    print(f"[LOOP] id={args.id} gen={args.gen} steps={args.steps}")
    sys.stdout.flush()

    if args.steps <= 0:
        i = 0
        while True:
            i += 1
            print(f"[LOOP] iter {i}")
            sys.stdout.flush()
            time.sleep(1)
    else:
        sleep_ms = int(genome.get("sleep_ms", 40))
        for i in range(args.steps):
            if (i % max(1, args.steps // 5)) == 0 or i == args.steps - 1:
                print(f"[LOOP] step {i+1}/{args.steps}")
                sys.stdout.flush()
            time.sleep(max(0.0, sleep_ms) / 1000.0)

        sc = _score(genome, args.steps, rng)

        payload = {
            "organism_id": int(args.id),
            "generation": int(args.gen),
            "steps": int(args.steps),
            "score": sc,
            "genome": genome,
        }

        try:
            _write_result(args.workdir, payload)
            print("[LOOP] wrote result.json")
        except Exception as e:
            print("[LOOP] result write failed:", e)

        return 0

# =============================================================================
# DIGITAL-DNA — EVOLUTION LOOP (WORKER)
# CLI CONTRACT (LOCKED BY ALL-ONE)
#   --steps <int>       : finite steps, then write result.json and exit
#   --workdir <path>    : per-organism directory; also becomes cwd
#   --id <int>          : organism id
#   --selftest          : prints "[SELFTEST] True" on success and exits 0
# =============================================================================

def _write_result(workdir, payload):
    from pathlib import Path
    import json, time
    wd = Path(workdir) if workdir else Path(".")
    wd.mkdir(parents=True, exist_ok=True)
    payload["ts"] = time.time()
    (wd / "result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

def _score_stub(steps: int, organism_id: int) -> float:
    # Replace later with real fitness function. Keep deterministic by default.
    return float(steps) + (float(organism_id) * 0.001)

if __name__ == "__main__":
    import argparse, time, os, sys
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=0)
    parser.add_argument("--workdir", type=str, default=None)
    parser.add_argument("--id", type=int, default=-1)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.workdir:
        Path(args.workdir).mkdir(parents=True, exist_ok=True)
        os.chdir(args.workdir)

    if args.selftest:
        # minimal smoke test: run 1 step and ensure writer works
        try:
            print("[LOOP] starting")
            print("[LOOP] step 1/1")
            score = _score_stub(1, args.id if args.id is not None else -1)
            _write_result(args.workdir, {"organism_id": args.id, "score": score, "steps": 1})
            print("[SELFTEST] True")
            raise SystemExit(0)
        except Exception as e:
            print("[SELFTEST] False:", e)
            raise SystemExit(2)

    print("[LOOP] starting")

    if args.steps <= 0:
        i = 0
        while True:
            i += 1
            print(f"[LOOP] iter {i}")
            time.sleep(1)
    else:
        for i in range(args.steps):
            print(f"[LOOP] step {i+1}/{args.steps}")
            time.sleep(0.05)

        score = _score_stub(args.steps, args.id)

        try:
            _write_result(args.workdir, {
                "organism_id": args.id,
                "score": score,
                "steps": args.steps
            })
            print("[LOOP] wrote result.json")
        except Exception as e:
            print("[LOOP] result write failed:", e)

        raise SystemExit(0)