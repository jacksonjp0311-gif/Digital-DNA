from __future__ import annotations

import os
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]

DENY_DIRS = {
    ".git",
    "__pycache__",
    "artifacts",
    "logs",
    "memory",
    "core_runtime",
    "ecosystem",
    "population",
    "organisms",
    "sandbox",
    "developer",
    "ddna_evo",
    "ddna_evolve",
    "codex",
    "_mutations",
    "_patch_backups",
    "_backups",
    "_backup_pre_allone_20260217_124846",
    "_backup_pre_d4",
}

DENY_PREFIXES = ("_backup",)
SPECIAL_SUBPATH_PREFIXES = {
    ("state", "candidates"),
    ("state", "history"),
    ("core_runtime",),
    ("ecosystem",),
    ("population",),
    ("organisms",),
    ("sandbox",),
}


def _normalize(name: str) -> str:
    return name.replace("\\", "/")


def _should_skip_dir(parent: Path, child: str) -> bool:
    lowered = child.lower()
    if lowered in DENY_DIRS:
        return True
    if any(lowered.startswith(prefix) for prefix in DENY_PREFIXES):
        return True

    if parent == ROOT:
        rel_parts_tuple: tuple[str, ...] = ()
    else:
        rel_parts_tuple = tuple(part for part in _normalize(parent.relative_to(ROOT).as_posix()).split("/") if part)
    rel_tuple = tuple(part.lower() for part in rel_parts_tuple)
    candidate = rel_tuple + (lowered,)

    for prefix in SPECIAL_SUBPATH_PREFIXES:
        if len(candidate) >= len(prefix) and candidate[: len(prefix)] == prefix:
            return True
    return False


def extract_genome(root: str | os.PathLike[str] | None = None) -> dict[str, List[str]]:
    """Return deterministic file list ("genome") for the repo."""
    if root is None:
        root_path = ROOT
    else:
        root_path = Path(root).resolve()

    out: List[str] = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        current = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not _should_skip_dir(current, d)]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            full = current / filename
            rel = _normalize(full.relative_to(root_path).as_posix())
            out.append(rel)

    out.sort()
    return {"files": out}
