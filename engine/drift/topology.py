import json
import os

ENGINE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASELINE_PATH = os.path.join(ENGINE_ROOT, "state", "environments", "topology_baseline.json")

def baseline_lock_enabled() -> bool:
    return os.getenv("DDNA_BASELINE_LOCK", "0").strip().lower() in {"1", "true", "yes", "on"}

def extract_topology():
    paths = []
    for root, dirs, files in os.walk(ENGINE_ROOT):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for filename in files:
            if filename.endswith(".py"):
                rel = os.path.relpath(os.path.join(root, filename), ENGINE_ROOT)
                paths.append(rel.replace("\\\\", "/"))
    return sorted(paths)

def load_baseline():
    if not os.path.exists(BASELINE_PATH):
        return None
    # tolerate accidental BOM
    with open(BASELINE_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_baseline(topology):
    os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(topology, f, indent=2)

def compute_topology_drift(current):
    baseline = load_baseline()
    if baseline is None:
        if baseline_lock_enabled():
            raise RuntimeError(
                "Topology baseline missing while DDNA_BASELINE_LOCK is enabled. "
                "Provision state/environments/topology_baseline.json."
            )
        save_baseline(current)
        return 0.0

    # Allow baseline stored as {fingerprint, files} or as raw list (legacy)
    if isinstance(baseline, dict):
        baseline = baseline.get("files", [])
    base = set(baseline)
    curr = set(current)

    if not base:
        return 0.0

    sym = base.symmetric_difference(curr)
    return len(sym) / len(base)
