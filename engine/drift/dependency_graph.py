import ast
import json
import os
from typing import Iterable, List, Optional, Set

ENGINE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASELINE_PATH = os.path.join(ENGINE_ROOT, "state", "environments", "dependency_baseline.json")

DENY_DIRS = {".git", "__pycache__", "developer", "_patch_backups", "_mutations"}
DENY_PREFIXES = ("_backup",)


def baseline_lock_enabled() -> bool:
    return os.getenv("DDNA_BASELINE_LOCK", "0").strip().lower() in {"1", "true", "yes", "on"}


def _normalize_edge(value: str) -> str:
    if not isinstance(value, str):
        return ""
    return value.replace("\\", "/")


def _normalize_graph(graph: Iterable[str]) -> List[str]:
    normalized = [_normalize_edge(edge) for edge in graph if edge]
    return sorted({edge for edge in normalized if edge})


def _should_skip_dir(name: str) -> bool:
    if name in DENY_DIRS:
        return True
    return any(name.startswith(prefix) for prefix in DENY_PREFIXES)


def _imports_from_file(py_path: str) -> Set[str]:
    edges: Set[str] = set()
    rel_src = os.path.relpath(py_path, ENGINE_ROOT).replace("\\", "/")

    try:
        with open(py_path, "r", encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
    except Exception:
        return edges

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                mod = (name.name or "").strip()
                if mod:
                    edges.add(f"{rel_src} -> {mod}")
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").strip()
            if mod:
                edges.add(f"{rel_src} -> {mod}")
    return edges


def extract_dependency_graph() -> List[str]:
    edges: Set[str] = set()
    for root, dirs, files in os.walk(ENGINE_ROOT):
        dirs[:] = [d for d in dirs if not _should_skip_dir(d)]
        for filename in files:
            if filename.endswith(".py"):
                full = os.path.join(root, filename)
                edges |= _imports_from_file(full)
    return _normalize_graph(edges)


def load_baseline() -> Optional[List[str]]:
    if not os.path.exists(BASELINE_PATH):
        return None
    with open(BASELINE_PATH, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, list):
        return _normalize_graph(data)
    return None


def save_baseline(graph: Iterable[str]) -> None:
    os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
    normalized = _normalize_graph(graph)
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2)


def compute_dependency_drift(current_graph: Iterable[str]) -> float:
    current = set(_normalize_graph(current_graph))
    baseline = load_baseline()

    if baseline is None:
        if baseline_lock_enabled():
            raise RuntimeError(
                "Dependency baseline missing while DDNA_BASELINE_LOCK is enabled. "
                "Provision state/environments/dependency_baseline.json."
            )
        save_baseline(current)
        return 0.0

    base = set(baseline)

    if not base and not current:
        return 0.0

    union = base | current
    if not union:
        return 0.0

    sym = base.symmetric_difference(current)
    drift = len(sym) / len(union)
    return max(0.0, min(1.0, float(drift)))
