from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_POLICY = {
    "min_stability": 0.84,
    "max_drift": 0.2,
    "max_topology_drift": 0.12,
    "max_dependency_drift": 0.15,
    "require_retention": 0.95,
}


@dataclass(frozen=True)
class GateResult:
    passed: bool
    violations: tuple[str, ...]
    policy: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "violations": list(self.violations),
            "policy": self.policy,
        }


def load_policy(path: str | Path | None = None) -> dict[str, float]:
    if path is None:
        return dict(DEFAULT_POLICY)
    policy_path = Path(path)
    if not policy_path.exists():
        return dict(DEFAULT_POLICY)
    raw = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("policy must be a JSON object")
    policy = dict(DEFAULT_POLICY)
    for key, value in raw.items():
        if key not in DEFAULT_POLICY:
            raise ValueError(f"unknown policy key: {key}")
        policy[key] = float(value)
    for key, value in policy.items():
        if value < 0:
            raise ValueError(f"policy key {key!r} must be non-negative")
    return policy


def evaluate_gate(record: dict[str, Any], policy: dict[str, float]) -> GateResult:
    checks = [
        ("stability", ">=", "min_stability", float(record["stability"]), policy["min_stability"]),
        ("drift", "<=", "max_drift", float(record["drift"]), policy["max_drift"]),
        (
            "drift_topology",
            "<=",
            "max_topology_drift",
            float(record["drift_topology"]),
            policy["max_topology_drift"],
        ),
        (
            "drift_dependency",
            "<=",
            "max_dependency_drift",
            float(record["drift_dependency"]),
            policy["max_dependency_drift"],
        ),
        ("retention", ">=", "require_retention", float(record["retention"]), policy["require_retention"]),
    ]
    violations: list[str] = []
    for metric, operator, policy_key, observed, expected in checks:
        failed = observed < expected if operator == ">=" else observed > expected
        if failed:
            violations.append(
                f"{metric} {observed:.6f} violates {policy_key} {operator} {expected:.6f}"
            )
    return GateResult(passed=not violations, violations=tuple(violations), policy=policy)


def attach_gate(record: dict[str, Any], gate: GateResult) -> dict[str, Any]:
    enriched = dict(record)
    enriched["gate"] = gate.to_dict()
    return enriched


def explain_record(record: dict[str, Any], gate: GateResult) -> str:
    status = "PASS" if gate.passed else "FAIL"
    lines = [
        "# Digital-DNA Gate Explanation",
        "",
        f"**Gate:** {status}",
        f"**Stability:** `{float(record['stability']):.6f}`",
        f"**Retention:** `{float(record['retention']):.6f}`",
        f"**Drift:** `{float(record['drift']):.6f}`",
        "",
        "## Policy",
        "",
        "| Constraint | Value |",
        "| --- | ---: |",
    ]
    for key in sorted(gate.policy):
        lines.append(f"| `{key}` | {gate.policy[key]:.6f} |")
    lines.extend(["", "## Result", ""])
    if gate.violations:
        lines.extend(f"- {violation}" for violation in gate.violations)
    else:
        lines.append("- All structural continuity constraints passed.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Digital-DNA measures structural continuity, not semantic correctness. A passing gate means the repository remains inside the configured genome, topology, dependency, retention, and drift envelope.",
        ]
    )
    return "\n".join(lines) + "\n"
