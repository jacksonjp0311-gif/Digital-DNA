# RCCT Kernel Overview

The `rcct_kernel/` folder contains auxiliary RCCT engine code, state snapshots, and RCCT-local logs/ledger.

## Mini Directory
- `rcct_engine.py` — RCCT kernel runtime.
- `rcct_state.json` + `state/` — current and historical RCCT state snapshots.
- `ledger/rcct_ledger.jsonl` — RCCT continuity ledger.
- `logs/` — per-run RCCT traces.

## Sequence of Events
1. RCCT engine executes and updates kernel state.
2. Snapshots/logs are persisted per run.
3. Ledger appends continuity records.

## Interlinking Notes
- RCCT is auxiliary to core DDNA engine flow.
- Keep RCCT outputs isolated from core orchestrator artifact contracts.
