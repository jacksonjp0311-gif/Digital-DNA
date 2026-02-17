from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

ENGINE_ROOT = Path(__file__).resolve().parents[2]

def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _read_bytes(p: Path) -> bytes:
    try:
        return p.read_bytes()
    except Exception:
        return b""

def compute_context_hash() -> str:
    """
    Hash of baseline+config files (NO-BOM UTF-8 expected).
    """
    parts = []
    targets = [
        ENGINE_ROOT / "state" / "environments" / "topology_baseline.json",
        ENGINE_ROOT / "state" / "environments" / "dependency_baseline.json",
        ENGINE_ROOT / "config" / "weights.json",
        ENGINE_ROOT / "config" / "thresholds.json",
    ]
    for t in targets:
        parts.append(t.as_posix().encode("utf-8") + b"::" + _read_bytes(t))
    return _sha256_bytes(b"||".join(parts))

def compute_repo_hash() -> str:
    """
    Best-effort git HEAD hash. Returns 'NO_GIT' if unavailable.
    """
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ENGINE_ROOT))
        return out.decode("utf-8", errors="ignore").strip() or "NO_GIT"
    except Exception:
        return "NO_GIT"

def read_thresholds() -> Dict[str, Any]:
    p = ENGINE_ROOT / "config" / "thresholds.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}