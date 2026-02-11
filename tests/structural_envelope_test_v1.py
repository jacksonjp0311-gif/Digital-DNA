import subprocess
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)

def run_ddna():
    # Run orchestrator cleanly
    subprocess.check_call(
        ["python", "-m", "engine.orchestrator.run_ddna"],
        cwd=ROOT
    )

    artifact_path = os.path.join(ROOT, "artifacts", "last_run.json")

    if not os.path.exists(artifact_path):
        raise RuntimeError("last_run.json not found after DDNA run")

    with open(artifact_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    baseline = run_ddna()

    assert_true("retention" in baseline, "Missing retention")
    assert_true("drift" in baseline, "Missing drift")
    assert_true("drift_raw" in baseline, "Missing drift_raw")
    assert_true("drift_topology" in baseline, "Missing drift_topology")
    assert_true("drift_dependency" in baseline, "Missing drift_dependency")
    assert_true("stability" in baseline, "Missing stability")

    # Envelope invariants
    assert_true(0.0 <= baseline["drift"] <= 1.0, "Drift out of bounds")
    assert_true(
        abs(baseline["drift"] - max(0.0, min(1.0, baseline["drift_raw"]))) < 1e-9,
        "Clamp invariant violated"
    )

    # Emit proof artifact
    proof = {
        "test": "structural_envelope_test_v1",
        "status": "PASS",
        "record": baseline
    }

    out_path = os.path.join(ROOT, "tests", "results", "structural_envelope_proof_v1.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(proof, f, indent=2)

    print("STRUCTURAL ENVELOPE TEST PASSED")

if __name__ == "__main__":
    main()
