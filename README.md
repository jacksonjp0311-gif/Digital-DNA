# Digital DNA (DDNA)

Digital DNA is a deterministic structural coherence engine that measures and enforces invariant stability across a software system.

---

## Core Model

DDNA computes structural stability through weighted drift channels:

drift_raw = (w_topology * drift_topology) + (w_dependency * drift_dependency)  
drift = clamp(drift_raw, 0, 1)  
stability = retention - drift  

All invariants are mathematically enforced and test-verified.

---

## Architecture

engine/
- genome/        → Structural extraction & normalization
- drift/         → Topology + dependency drift computation
- stability/     → Retention and stability law
- orchestrator/  → Execution entry point
- ledger/        → Artifact recording

config/
- weights.json   → Active drift channel weights (UTF-8 no BOM)

state/
- environments/  → Baseline structural snapshots

artifacts/
- last_run.json  → Deterministic execution output

tests/
- behavioral_test_v1.py
- structural_envelope_test_v1.py
- results/

---

## Guarantees

✓ Deterministic execution  
✓ Artifact-based testing (no stdout parsing)  
✓ Hard invariant enforcement  
✓ Drift bounded in [0,1]  
✓ Stability law verified  
✓ UTF-8 clean configuration  
✓ Test suite passing  

---

## Execution

Run engine:

    python -m engine.orchestrator.run_ddna

Run tests:

    python tests/behavioral_test_v1.py
    python tests/structural_envelope_test_v1.py

---

## Current Status

Core Lock v1 — Stable, invariant-verified engine with full test coverage on structural envelope and behavioral constraints.

---

## Author

James Paul Jackson

███████████████████████████████████████████████████████████████████████████████