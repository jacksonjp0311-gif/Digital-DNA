from __future__ import annotations
import json, subprocess, sys, time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "engine" / "evolution" / "evolution_loop.py"

@dataclass
class EcoConfig:
    population: int = 6
    steps_per_org: int = 1
    elite_keep: int = 2

def run_generation(gen: int, cfg: EcoConfig):
    eco_root = ROOT / "state" / "ecosystem"
    org_root = eco_root / "organisms"
    out_root = eco_root / "results"
    ledger = eco_root / "ledger" / "ecosystem_ledger.jsonl"

    org_root.mkdir(parents=True, exist_ok=True)
    out_root.mkdir(parents=True, exist_ok=True)

    results = []

    for i in range(cfg.population):
        org_id = f"org_{i:04d}"
        workdir = org_root / org_id
        outpath = out_root / f"gen_{gen:06d}_{org_id}.json"

        workdir.mkdir(parents=True, exist_ok=True)

        subprocess.run([
            sys.executable, str(ENGINE),
            "--steps", str(cfg.steps_per_org),
            "--out", str(outpath),
            "--workdir", str(workdir)
        ])

        if outpath.exists():
            r = json.loads(outpath.read_text())
        else:
            r = {"best_score": -999}

        r["org"] = org_id
        r["gen"] = gen
        results.append(r)

        with open(ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(r) + "\n")

    return results

def ecosystem_loop(cfg: EcoConfig, generations: int = 20):
    best = None
    for g in range(generations):
        results = run_generation(g, cfg)
        results.sort(key=lambda x: x.get("best_score", -999), reverse=True)
        best = results[0]
        print(f"GEN {g} BEST:", best.get("best_score"))

    return best
