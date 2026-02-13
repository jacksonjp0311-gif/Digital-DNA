import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)

def run_engine():
    subprocess.check_call([sys.executable, str(ROOT / "engine" / "orchestrator" / "run_ddna.py")], cwd=str(ROOT))
    p = ROOT / "artifacts" / "last_run.json"
    assert_true(p.exists(), "artifacts/last_run.json missing")
    return json.loads(p.read_text(encoding="utf-8"))

def run_loop():
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "ddna_loop.py")], cwd=str(ROOT))
    p = ROOT / "docs" / "feedback" / "packet_latest.json"
    assert_true(p.exists(), "docs/feedback/packet_latest.json missing")
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    # prefer unlocked for initial baseline provisioning
    os.environ.setdefault("DDNA_BASELINE_LOCK", "0")

    rec = run_engine()

    # schema assertions
    for k in [
        "retention","drift_total","drift_topology","drift_dependency","stability","timestamp",
        "context_hash","repo_hash","boundary_score","boundary_event","boundary_reason","replay_K","Bcrit"
    ]:
        assert_true(k in rec, f"missing key: {k}")

    # invariant: stability = retention - drift_total
    expected = float(rec["retention"]) - float(rec["drift_total"])
    assert_true(abs(expected - float(rec["stability"])) < 1e-9, "stability invariant violated")

    # boundary score bounds
    bs = float(rec["boundary_score"])
    assert_true(0.0 <= bs <= 1.0, "boundary_score out of bounds")

    pkt = run_loop()
    assert_true("episode" in pkt and "observations" in pkt and "replay" in pkt, "packet missing sections")
    assert_true(pkt["observations"]["stability"] is not None, "packet stability missing")
    assert_true((ROOT / "artifacts" / "replay_k.json").exists(), "replay_k.json missing")

    print("EPISODIC_TEST_V1 PASSED")

if __name__ == "__main__":
    main()