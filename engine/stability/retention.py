from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Any

from engine.genome.fingerprint import fingerprint_genome

ENGINE_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = ENGINE_ROOT / "state" / "genomes" / "baseline.json"

def baseline_lock_enabled() -> bool:
    return os.getenv("DDNA_BASELINE_LOCK", "0").strip().lower() in {"1", "true", "yes", "on"}

def load_baseline() -> Dict[str, Any] | None:
    if not BASELINE_PATH.exists():
        return None
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

def save_baseline(obj: Dict[str, Any]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def compute_retention(genome: Dict[str, Any]) -> float:
    """
    Retention in [0,1]:
      1.0 when current genome fingerprint matches baseline fingerprint
      else overlap score based on file list Jaccard + symbol overlap.
    """
    base = load_baseline()
    cur_fp = fingerprint_genome(genome)

    if base is None:
        if baseline_lock_enabled():
            raise RuntimeError(
                "Genome baseline missing while DDNA_BASELINE_LOCK is enabled. "
                "Provision state/genomes/baseline.json."
            )
        # initialize baseline
        save_baseline({
            "schema": "ddna.genome_baseline.v1",
            "fingerprint": cur_fp,
            "files": genome.get("files", []),
            "symbols": genome.get("symbols", {}),
        })
        return 1.0

    base_fp = str(base.get("fingerprint", ""))
    if base_fp and base_fp == cur_fp:
        return 1.0

    # Jaccard over files
    base_files = set(base.get("files", []) or [])
    cur_files = set(genome.get("files", []) or [])
    if not base_files and not cur_files:
        return 1.0

    inter = len(base_files.intersection(cur_files))
    union = max(1, len(base_files.union(cur_files)))
    j_files = inter / union

    # Symbol overlap (names only)
    base_syms = base.get("symbols", {}) or {}
    cur_syms = genome.get("symbols", {}) or {}

    sym_inter = 0
    sym_union = 0
    for k in set(base_syms.keys()).union(set(cur_syms.keys())):
        a = set(base_syms.get(k, []) or [])
        b = set(cur_syms.get(k, []) or [])
        sym_inter += len(a.intersection(b))
        sym_union += len(a.union(b))
    j_sym = (sym_inter / sym_union) if sym_union > 0 else 1.0

    # Conservative blend
    r = 0.7 * j_files + 0.3 * j_sym
    # clamp
    if r < 0.0: r = 0.0
    if r > 1.0: r = 1.0
    return float(r)