from __future__ import annotations
from pathlib import Path
import ast
from typing import Dict, Any, List

def _safe_parse(path: Path):
    try:
        txt = path.read_text(encoding="utf-8")
        return ast.parse(txt), txt
    except Exception:
        return None, None

def extract_genome(root: Path | None = None) -> Dict[str, Any]:
    """
    Deterministic repo structural genome.
    - files: relative .py paths (sorted)
    - symbols: per-file top-level defs/classes (names only; sorted)
    """
    if root is None:
        root = Path.cwd()
    root = Path(root).resolve()

    py_files: List[Path] = []
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        py_files.append(p)

    rel_files = sorted([p.relative_to(root).as_posix() for p in py_files])

    symbols = {}
    for p in py_files:
        tree, _txt = _safe_parse(p)
        rel = p.relative_to(root).as_posix()
        names = []
        if tree is not None:
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.append(node.name)
        symbols[rel] = sorted(set(names))

    genome = {
        "root": str(root),
        "files": rel_files,
        "symbols": symbols,
        "schema": "ddna.genome.v1"
    }
    return genome