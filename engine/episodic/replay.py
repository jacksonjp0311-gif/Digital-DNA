from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

ENGINE_ROOT = Path(__file__).resolve().parents[2]
HIST = ENGINE_ROOT / "artifacts" / "history"
REPLAY_OUT = ENGINE_ROOT / "artifacts" / "replay_k.json"

def _read_json(p: Path) -> Dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _linear_slope(xs: List[float]) -> float:
    # simple slope over index: cov(i,x)/var(i)
    n = len(xs)
    if n < 2:
        return 0.0
    idx = list(range(n))
    mean_i = sum(idx) / n
    mean_x = sum(xs) / n
    cov = sum((idx[i]-mean_i)*(xs[i]-mean_x) for i in range(n))
    var = sum((idx[i]-mean_i)*(idx[i]-mean_i) for i in range(n))
    return float(cov / var) if var > 0 else 0.0

def compute_replay_summary(k: int = 10) -> Dict[str, Any]:
    files = sorted(HIST.glob("run_*.json"))
    tail = files[-k:] if len(files) > k else files[:]
    records = [_read_json(p) for p in tail]

    stabs = []
    for r in records:
        try:
            stabs.append(float(r.get("stability", 0.0)))
        except Exception:
            stabs.append(0.0)

    if not stabs:
        summary = {
            "K": k,
            "count": 0,
            "mean_stability": None,
            "last_stability": None,
            "delta": None,
            "slope": None,
            "min": None,
            "max": None,
            "path": str(REPLAY_OUT.relative_to(ENGINE_ROOT)).replace("\\","/")
        }
        return summary

    mean = sum(stabs)/len(stabs)
    last = stabs[-1]
    prev = stabs[-2] if len(stabs) >= 2 else last
    summary = {
        "K": int(k),
        "count": int(len(stabs)),
        "mean_stability": float(mean),
        "last_stability": float(last),
        "delta": float(last - prev),
        "slope": float(_linear_slope(stabs)),
        "min": float(min(stabs)),
        "max": float(max(stabs)),
        "path": str(REPLAY_OUT.relative_to(ENGINE_ROOT)).replace("\\","/")
    }
    return summary

def write_replay_summary(k: int = 10) -> Dict[str, Any]:
    out = compute_replay_summary(k)
    REPLAY_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPLAY_OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out