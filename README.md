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

## Theory

DDNA includes canonical theory documents under `theory/` that formalize the structural replication model, drift-bounded stability, and ledger-anchored continuity:

- `theory/digital_dna_software_theory_v1_3.tex` (DDNA v1.3 · Locked Evolution)
- `theory/codex_digital_dna_theory_memory_architecture_v1_6.tex` (DDNA v1.6 · Locked)
- `theory/README.md` for the mini directory and interlinking overview

---

## Evaluation and Continuity

- Iteration evaluation and roadmap: `docs/ARCHITECTURE_EVALUATION.md`
- Codex continuity log for every upgrade/session: `docs/CODEX_UPGRADE_LOG.md`

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
