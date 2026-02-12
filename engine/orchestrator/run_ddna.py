import json
import os
from datetime import datetime, timezone

from engine.drift.dependency_graph import compute_dependency_drift, extract_dependency_graph
from engine.drift.topology import compute_topology_drift, extract_topology
from engine.genome.compare import compare_genomes
from engine.genome.extract import extract_genome
from engine.ledger.append import append_ledger
from engine.orchestrator.validation import validate_record, validate_weights
from engine.stability.compute_S import compute_stability
from engine.stability.retention import retention_ratio

BASELINE_PATH = "state/genomes/baseline.json"
LEDGER_PATH = "ledger/ddna_ledger.jsonl"
WEIGHTS_PATH = "config/weights.json"
OUTPUT_PATH = "artifacts/last_run.json"


def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def baseline_lock_enabled() -> bool:
    return os.getenv("DDNA_BASELINE_LOCK", "0").strip().lower() in {"1", "true", "yes", "on"}


def load_weights() -> tuple[float, float]:
    if not os.path.exists(WEIGHTS_PATH):
        return 1.0, 1.0

    with open(WEIGHTS_PATH, "r", encoding="utf-8") as f:
        weights = json.load(f)

    return validate_weights(weights)


def load_or_init_genome_baseline(current):
    if os.path.exists(BASELINE_PATH):
        with open(BASELINE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    if baseline_lock_enabled():
        raise RuntimeError(
            "Genome baseline missing while DDNA_BASELINE_LOCK is enabled. "
            "Provision baseline at state/genomes/baseline.json."
        )

    baseline = current
    os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
    return baseline


def run(_target_path="."):
    current = extract_genome()
    baseline = load_or_init_genome_baseline(current)

    common = compare_genomes(current, baseline)
    retention = retention_ratio(common, len(baseline))

    topology = extract_topology()
    dependency_graph = extract_dependency_graph()

    drift_topology = float(compute_topology_drift(topology))
    drift_dependency = float(compute_dependency_drift(dependency_graph))

    weight_topology, weight_dependency = load_weights()

    drift_raw = float((weight_topology * drift_topology) + (weight_dependency * drift_dependency))
    drift = float(clamp01(drift_raw))

    stability = compute_stability(retention, drift)

    record = {
        "retention": retention,
        "drift": drift,
        "drift_raw": drift_raw,
        "drift_topology": drift_topology,
        "drift_dependency": drift_dependency,
        "weights": {"topology": weight_topology, "dependency": weight_dependency},
        "stability": stability,
        "timestamp": utc_now_z(),
    }

    validate_record(record)

    append_ledger(LEDGER_PATH, record)

    os.makedirs("artifacts", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    print("DDNA RUN COMPLETE")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    run(".")
