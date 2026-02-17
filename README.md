# Digital DNA (DDNA)

Digital DNA is a deterministic structural coherence engine that measures and enforces invariant stability across a software system.

---

## Core Model

DDNA computes structural stability through weighted drift channels:

`drift_raw = (w_topology * drift_topology) + (w_dependency * drift_dependency)`
`drift = clamp(drift_raw, 0, 1)`
`stability = retention - drift`

All invariants are mathematically enforced and test-verified.

---

## Folder Mini-README System

Every top-level project folder includes its own local `README.md` (mini README), so each scope can be understood in-place without scanning the entire repository first.

### How to use mini READMEs (Human workflow)
1. Start in the folder you need to modify (`engine/`, `docs/`, `tools/`, etc.).
2. Read that folder’s `README.md` first for scope, sequence-of-events, and cross-links.
3. Follow links/filenames listed in the mini directory to jump directly to relevant files.

### How to use mini READMEs (AI workflow)
1. Treat each folder `README.md` as the local contract before editing files in that scope.
2. Use mini-directory and sequence sections to preserve deterministic execution order and truth-surface invariants.
3. Use interlinking notes to avoid out-of-scope state, bypassing orchestrator contracts, or introducing shadow pipelines.

### Top-level mini README coverage
- `artifacts/`
- `docs/`
- `engine/`
- `ledger/`
- `tools/` (script-equivalent utilities)
- plus runtime/support scopes: `config/`, `state/`, `tests/`, `theory/`, `interface/`, `logs/`, `memory/`, `genome/`, `rcct_kernel/`, `developer/`, `ddna_evo/`, `DDNA_EVOLVE/`, `_mutations/`, `_patch_backups/`.

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

## Execution

Run engine:

    python -m engine.orchestrator.run_ddna

Run tests:

    python tests/behavioral_test_v1.py
    python tests/structural_envelope_test_v1.py
    python tests/hardening_test_v2.py

Optional strict baseline policy (CI-friendly):

    DDNA_BASELINE_LOCK=1 python -m engine.orchestrator.run_ddna
