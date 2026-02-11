import os
import json

ENGINE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

BASELINE_PATH = os.path.join(
    ENGINE_ROOT, "state", "environments", "topology_baseline.json"
)

def extract_topology():
    paths = []

    for root, dirs, files in os.walk(ENGINE_ROOT):
        for f in files:
            if f.endswith(".py"):
                rel = os.path.relpath(
                    os.path.join(root, f),
                    ENGINE_ROOT
                )
                paths.append(rel.replace("\\\\", "/"))

    return sorted(paths)

def load_baseline():
    if not os.path.exists(BASELINE_PATH):
        return None
    with open(BASELINE_PATH, "r") as f:
        return json.load(f)

def save_baseline(topology):
    os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
    with open(BASELINE_PATH, "w") as f:
        json.dump(topology, f, indent=2)

def compute_topology_drift(current):
    baseline = load_baseline()

    if baseline is None:
        save_baseline(current)
        return 0.0

    base_set = set(baseline)
    curr_set = set(current)

    symmetric_diff = base_set.symmetric_difference(curr_set)

    if len(base_set) == 0:
        return 0.0

    return len(symmetric_diff) / len(base_set)
