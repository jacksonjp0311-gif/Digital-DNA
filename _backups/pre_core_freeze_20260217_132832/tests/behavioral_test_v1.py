import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run_ddna():
    subprocess.run(
        [sys.executable, "-m", "engine.orchestrator.run_ddna"],
        check=True,
        cwd=ROOT
    )
    with open(ROOT / "artifacts" / "last_run.json", "r") as f:
        return json.load(f)

def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)

def main():
    record = run_ddna()

    assert_true("retention" in record, "Missing retention")
    assert_true("drift" in record, "Missing drift")
    assert_true("drift_raw" in record, "Missing drift_raw")
    assert_true("stability" in record, "Missing stability")

    expected = record["retention"] - record["drift"]
    assert_true(abs(expected - record["stability"]) < 1e-6,
                "Stability invariant violated")

    print("BEHAVIORAL TEST PASSED")

if __name__ == "__main__":
    main()
