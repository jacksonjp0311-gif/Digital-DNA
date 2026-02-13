from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class BoundaryResult:
    boundary_score: float
    boundary_event: bool
    reason: str

def compute_boundary(context_hash_prev: Optional[str],
                     context_hash_now: str,
                     repo_hash_prev: Optional[str],
                     repo_hash_now: str,
                     drift_total: float,
                     bcrit: float) -> BoundaryResult:
    score = 0.0
    reasons = []

    if context_hash_prev and context_hash_prev != context_hash_now:
        score += 0.6
        reasons.append("context_hash_changed")

    if repo_hash_prev and repo_hash_prev != repo_hash_now and repo_hash_now != "NO_GIT":
        score += 0.3
        reasons.append("repo_hash_changed")

    # drift cue (bounded contribution)
    try:
        dt = float(drift_total)
    except Exception:
        dt = 0.0
    score += min(0.2, max(0.0, dt))  # small additive cue

    # clamp
    if score < 0.0: score = 0.0
    if score > 1.0: score = 1.0

    event = bool(score > float(bcrit))
    if event:
        reasons.append("boundary_triggered")

    return BoundaryResult(boundary_score=float(score),
                          boundary_event=event,
                          reason=",".join(reasons) if reasons else "none")