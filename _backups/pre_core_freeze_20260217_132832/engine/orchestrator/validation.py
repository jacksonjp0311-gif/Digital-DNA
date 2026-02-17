import math
from typing import Any, Dict, Tuple

EXPECTED_WEIGHT_KEYS = {"topology", "dependency"}


def validate_weights(weights: Dict[str, Any]) -> Tuple[float, float]:
    if not isinstance(weights, dict):
        raise ValueError("weights.json must be a JSON object")

    unknown = set(weights.keys()) - EXPECTED_WEIGHT_KEYS
    if unknown:
        raise ValueError(f"weights.json contains unknown keys: {sorted(unknown)}")

    missing = EXPECTED_WEIGHT_KEYS - set(weights.keys())
    if missing:
        raise ValueError(f"weights.json missing required keys: {sorted(missing)}")

    wt = float(weights["topology"])
    wd = float(weights["dependency"])

    for k, v in (("topology", wt), ("dependency", wd)):
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"weight '{k}' must be finite")
        if v < 0.0:
            raise ValueError(f"weight '{k}' must be >= 0")
        if v > 10.0:
            raise ValueError(f"weight '{k}' must be <= 10")

    return wt, wd


def validate_record(record: Dict[str, Any]) -> None:
    required = {
        "retention",
        "drift",
        "drift_raw",
        "drift_topology",
        "drift_dependency",
        "weights",
        "stability",
        "timestamp",
    }
    missing = sorted(required - set(record.keys()))
    if missing:
        raise ValueError(f"record missing required keys: {missing}")

    drift = float(record["drift"])
    if drift < 0.0 or drift > 1.0:
        raise ValueError("record drift must be in [0, 1]")

    expected_stability = float(record["retention"]) - drift
    if abs(expected_stability - float(record["stability"])) > 1e-9:
        raise ValueError("stability invariant violated: stability != retention - drift")
