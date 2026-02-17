from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = ROOT / "state" / "environments" / "topology_baseline.json"

def baseline_lock_enabled() -> bool:
    return os.environ.get("DDNA_BASELINE_LOCK", "0") == "1"

def load_baseline():
    if not BASELINE_PATH.exists():
        return None
    txt = BASELINE_PATH.read_text(encoding="utf-8").strip()
    if not txt:
        return None
    return json.loads(txt)

def save_baseline(files_list):
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    obj = {"files": list(files_list)}
    BASELINE_PATH.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def extract_topology():
    """
    Returns: list[str]
    Used by orchestrator import: from engine.drift.topology import extract_topology
    """
    try:
        from engine.genome.extract import extract_genome
        g = extract_genome()
        return list(g.get("files", []))
    except Exception:
        files = []
        for p in ROOT.rglob("*.py"):
            s = str(p).replace("\\", "/")
            if "/.git/" in s or "/__pycache__/" in s or "/developer/" in s:
                continue
            files.append(str(p.relative_to(ROOT)).replace("\\", "/"))
        files.sort()
        return files

def compute_topology_drift(current):
    """
    current: list[str] (topology list)
    Returns drift in [0,1] using |Δ| / |union|
    """
    baseline = load_baseline()

    if baseline is None:
        if baseline_lock_enabled():
            raise RuntimeError(
                "Topology baseline missing/empty while DDNA_BASELINE_LOCK=1. "
                "Rebuild state/environments/topology_baseline.json"
            )
        save_baseline(current)
        return 0.0

    base_files = baseline.get("files", [])
    base = set(base_files or [])
    curr = set(current or [])

    if not base and not curr:
        return 0.0

    union = base | curr
    if not union:
        return 0.0

    diff = base.symmetric_difference(curr)
    drift = len(diff) / len(union)

    if drift < 0:
        drift = 0.0
    if drift > 1:
        drift = 1.0
    return float(drift)