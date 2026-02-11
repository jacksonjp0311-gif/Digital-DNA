import os
import json
import ast

ENGINE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

BASELINE_PATH = os.path.join(
    ENGINE_ROOT, "state", "environments", "dependency_baseline.json"
)

def _imports_from_file(py_path: str):
    edges = set()
    rel_src = os.path.relpath(py_path, ENGINE_ROOT).replace("\\\\", "/")

    try:
        with open(py_path, "r", encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
    except Exception:
        return edges

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mod = (n.name or "").strip()
                if mod:
                    edges.add(f"{rel_src} -> {mod}")
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").strip()
            if mod:
                edges.add(f"{rel_src} -> {mod}")

    return edges

def extract_dependency_graph():
    edges = set()
    for root, dirs, files in os.walk(ENGINE_ROOT):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                full = os.path.join(root, f)
                edges |= _imports_from_file(full)
    return sorted(edges)

def load_baseline():
    if not os.path.exists(BASELINE_PATH):
        return None
    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_baseline(graph):
    os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

def compute_dependency_drift(current_graph):
    baseline = load_baseline()
    if baseline is None:
        save_baseline(current_graph)
        return 0.0

    base = set(baseline)
    curr = set(current_graph)
    if len(base) == 0:
        return 0.0

    sym = base.symmetric_difference(curr)
    return len(sym) / len(base)
