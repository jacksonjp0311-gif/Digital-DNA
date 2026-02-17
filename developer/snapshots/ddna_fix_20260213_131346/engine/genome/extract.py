from __future__ import annotations
import os

def extract_genome(root=None):
    if root is None:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    files = []

    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath or "developer" in dirpath:
            continue

        for f in filenames:
            if f.endswith(".py"):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, root).replace("\\","/")
                files.append(rel)

    files.sort()
    return {"files": files}
