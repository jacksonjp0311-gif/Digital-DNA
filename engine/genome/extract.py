from __future__ import annotations
import os

def extract_genome(root=None):
    """
    Genome extraction (local-stable):
    - returns dict: {"files":[...]}
    - excludes: .git, __pycache__, developer
    - currently tracks .py only (you can broaden later)
    """
    if root is None:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    else:
        root = os.path.abspath(root)

    deny_dirs = {".git", "__pycache__", "developer"}
    out = []

    for dirpath, dirnames, filenames in os.walk(root):
        # prune denied dirs (exact dir names)
        dirnames[:] = [d for d in dirnames if d not in deny_dirs]

        for f in filenames:
            if not f.endswith(".py"):
                continue
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, root).replace("\\", "/")
            out.append(rel)

    out.sort()
    return {"files": out}


