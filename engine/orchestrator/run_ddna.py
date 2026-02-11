import os
import json
from datetime import datetime, timezone

from engine.genome.extract import extract_genome
from engine.genome.compare import compare_genomes

from engine.drift.topology import extract_topology, compute_topology_drift
from engine.drift.dependency_graph import extract_dependency_graph, compute_dependency_drift

from engine.stability.compute_S import compute_stability
from engine.stability.retention import retention_ratio

from engine.ledger.append import append_ledger

BASELINE_PATH = "state/genomes/baseline.json"
LEDGER_PATH   = "ledger/ddna_ledger.jsonl"
WEIGHTS_PATH  = "config/weights.json"
OUTPUT_PATH   = "artifacts/last_run.json"


def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def load_weights():
    wt = 1.0
    wd = 1.0
    if os.path.exists(WEIGHTS_PATH):
        with open(WEIGHTS_PATH, "r", encoding="utf-8") as f:
            w = json.load(f)
        wt = float(w.get("topology", 1.0))
        wd = float(w.get("dependency", 1.0))
    return wt, wd


def run(_target_path="."):

    # ───────────────────────── Genome Retention
    current = extract_genome()

    if os.path.exists(BASELINE_PATH):
        with open(BASELINE_PATH, "r", encoding="utf-8") as f:
            baseline = json.load(f)
    else:
        baseline = current
        os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
        with open(BASELINE_PATH, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)

    common = compare_genomes(current, baseline)
    C = retention_ratio(common, len(baseline))

    # ───────────────────────── Drift Channels
    topo = extract_topology()
    depg = extract_dependency_graph()

    D_topo = float(compute_topology_drift(topo))
    D_dep  = float(compute_dependency_drift(depg))

    wt, wd = load_weights()

    drift_raw = float((wt * D_topo) + (wd * D_dep))
    D = float(clamp01(drift_raw))

    # ───────────────────────── Stability
    S = compute_stability(C, D)

    record = {
        "retention": C,
        "drift": D,
        "drift_raw": drift_raw,
        "drift_topology": D_topo,
        "drift_dependency": D_dep,
        "weights": {
            "topology": wt,
            "dependency": wd
        },
        "stability": S,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # ───────────────────────── Ledger Append
    append_ledger(LEDGER_PATH, record)

    # ───────────────────────── Output Contract
    os.makedirs("artifacts", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    # ───────────────────────── Console Output
    print("DDNA RUN COMPLETE")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    run(".")
