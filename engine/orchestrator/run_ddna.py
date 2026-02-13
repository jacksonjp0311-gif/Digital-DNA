from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# ensure repo root is on path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.genome.extract import extract_genome
from engine.drift.topology import extract_topology, compute_topology_drift
from engine.drift.dependency_graph import extract_dependency_graph, compute_dependency_drift
from engine.stability.retention import compute_retention
from engine.episodic.context import compute_context_hash, compute_repo_hash, read_thresholds
from engine.episodic.replay import write_replay_summary
from engine.episodic.boundary import compute_boundary

ART = ROOT / "artifacts"
HIST = ART / "history"
LAST = ART / "last_run.json"
LAST_EP = ART / "last_episode.json"

def _read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def _write_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def main():
    thresholds = read_thresholds()
    Bcrit = float(thresholds.get("Bcrit", 0.5))
    K = int(thresholds.get("replay_K", 10))

    genome = extract_genome(ROOT)
    topo = extract_topology()
    depg = extract_dependency_graph()

    drift_topology = float(compute_topology_drift(topo))
    drift_dependency = float(compute_dependency_drift(depg))
    drift_total = drift_topology + drift_dependency

    retention = float(compute_retention(genome))
    stability = retention - drift_total

    context_hash = compute_context_hash()
    repo_hash = compute_repo_hash()

    prev = _read_json(LAST_EP) or {}
    prev_context = prev.get("context_hash")
    prev_repo = prev.get("repo_hash")

    b = compute_boundary(prev_context, context_hash, prev_repo, repo_hash, drift_total, Bcrit)

    # episode record (engine-level)
    out = {
        "retention": retention,
        "drift_total": drift_total,
        "drift_topology": drift_topology,
        "drift_dependency": drift_dependency,
        "stability": float(stability),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context_hash": context_hash,
        "repo_hash": repo_hash,
        "boundary_score": b.boundary_score,
        "boundary_event": b.boundary_event,
        "boundary_reason": b.reason,
        "replay_K": K,
        "Bcrit": Bcrit
    }

    ART.mkdir(exist_ok=True)
    HIST.mkdir(parents=True, exist_ok=True)

    _write_json(LAST, out)
    _write_json(LAST_EP, {"context_hash": context_hash, "repo_hash": repo_hash})

    # replay summary (over history) gets written by loop after snapshot exists,
    # but we also compute a current replay snapshot for convenience.
    # If history is empty, replay_k will be count=0.
    replay = write_replay_summary(K)
    out["replay_path"] = replay.get("path")

    print("DDNA RUN COMPLETE")
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()