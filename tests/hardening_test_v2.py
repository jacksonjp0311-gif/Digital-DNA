import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.orchestrator import run_ddna
from engine.orchestrator.validation import validate_record, validate_weights


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def test_validate_weights():
    wt, wd = validate_weights({"topology": 1.0, "dependency": 0.5})
    assert_true(wt == 1.0 and wd == 0.5, "Valid weights should parse")

    try:
        validate_weights({"topology": -1.0, "dependency": 1.0})
        raise AssertionError("Negative weights should fail")
    except ValueError:
        pass

    try:
        validate_weights({"topology": 1.0})
        raise AssertionError("Missing dependency key should fail")
    except ValueError:
        pass


def test_validate_record():
    record = {
        "retention": 0.9,
        "drift": 0.2,
        "drift_raw": 0.2,
        "drift_topology": 0.2,
        "drift_dependency": 0.0,
        "weights": {"topology": 1.0, "dependency": 1.0},
        "stability": 0.7,
        "timestamp": "2026-02-12T00:00:00Z",
    }
    validate_record(record)


def test_baseline_lock_for_genome_baseline():
    original_path = run_ddna.BASELINE_PATH
    original_lock = os.environ.get("DDNA_BASELINE_LOCK")

    try:
        with tempfile.TemporaryDirectory() as td:
            run_ddna.BASELINE_PATH = os.path.join(td, "missing", "baseline.json")
            os.environ["DDNA_BASELINE_LOCK"] = "1"
            try:
                run_ddna.load_or_init_genome_baseline(["abc"])
                raise AssertionError("Lock mode should reject missing baseline")
            except RuntimeError:
                pass
    finally:
        run_ddna.BASELINE_PATH = original_path
        if original_lock is None:
            os.environ.pop("DDNA_BASELINE_LOCK", None)
        else:
            os.environ["DDNA_BASELINE_LOCK"] = original_lock


def main():
    test_validate_weights()
    test_validate_record()
    test_baseline_lock_for_genome_baseline()
    print("HARDENING TEST V2 PASSED")


if __name__ == "__main__":
    main()
