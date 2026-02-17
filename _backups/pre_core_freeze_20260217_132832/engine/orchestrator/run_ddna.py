from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.drift.dependency_graph import compute_dependency_drift, extract_dependency_graph
from engine.drift.topology import compute_topology_drift, extract_topology
from engine.genome.extract import extract_genome
from engine.orchestrator.validation import validate_record, validate_weights
from engine.stability.retention import compute_retention

ARTIFACT_PATH = ROOT / "artifacts" / "last_run.json"
WEIGHTS_PATH = ROOT / "config" / "weights.json"
BASELINE_PATH = ROOT / "state" / "genomes" / "baseline.json"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_or_init_genome_baseline(files: list[str]) -> dict[str, list[str]]:
    lock_enabled = os.environ.get("DDNA_BASELINE_LOCK", "0") == "1"

    baseline_path = Path(BASELINE_PATH)

    if baseline_path.exists() and baseline_path.stat().st_size > 0:
        loaded = _read_json(baseline_path)
        if isinstance(loaded, dict) and isinstance(loaded.get("files"), list):
            return {"files": list(loaded["files"])}

    if lock_enabled:
        raise RuntimeError(
            "Genome baseline missing/empty while DDNA_BASELINE_LOCK=1. "
            "Rebuild state/genomes/baseline.json"
        )

    baseline = {"files": sorted(set(files))}
    _write_json(baseline_path, baseline)
    return baseline


def _load_weights() -> dict[str, float]:
    weights = _read_json(WEIGHTS_PATH)
    wt, wd = validate_weights(weights)
    return {"topology": wt, "dependency": wd}


def main() -> None:
    genome = extract_genome(ROOT)
    genome_files = list(genome.get("files", []))
    load_or_init_genome_baseline(genome_files)

    topology = extract_topology()
    dependency_graph = extract_dependency_graph()

    drift_topology = float(compute_topology_drift(topology))
    drift_dependency = float(compute_dependency_drift(dependency_graph))

    weights = _load_weights()

    drift_raw = (
        weights["topology"] * drift_topology
        + weights["dependency"] * drift_dependency
    )
    drift = max(0.0, min(1.0, float(drift_raw)))

    retention = float(compute_retention(ROOT, ROOT))
    stability = retention - drift

    record = {
        "retention": retention,
        "drift": drift,
        "drift_raw": drift_raw,
        "drift_topology": drift_topology,
        "drift_dependency": drift_dependency,
        "weights": weights,
        "stability": stability,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    validate_record(record)
    _write_json(ARTIFACT_PATH, record)

    print(f"stability: {stability:.6f}")


if __name__ == "__main__":
    main()
