from __future__ import annotations
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "state" / "environments" / "topology_baseline.json"

def load_baseline():
    if not BASELINE.exists():
        return None
    txt = BASELINE.read_text().strip()
    if not txt:
        return None
    return json.loads(txt)

def save_baseline(files):
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps({"files": files}, indent=2))

def extract_topology():
    try:
        from engine.genome.extract import extract_genome
        g = extract_genome()
        return g.get("files", [])
    except Exception:
        return []

def compute_topology_drift(current):
    baseline = load_baseline()

    if baseline is None:
        save_baseline(current)
        return 0.0

    base = set(baseline.get("files", []))
    curr = set(current)

    union = base | curr
    diff = base.symmetric_difference(curr)

    if not union:
        return 0.0

    drift = len(diff) / len(union)

    if drift < 0: drift = 0
    if drift > 1: drift = 1

    return float(drift)
