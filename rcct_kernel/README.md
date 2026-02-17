# RCCT Kernel Mini-README

Auxiliary RCCT runtime state and logs.

## Layout
- `rcct_engine.py` — RCCT kernel script.
- `rcct_state.json` + `state/` — persisted RCCT state snapshots.
- `ledger/` — RCCT ledger stream.
- `logs/` — RCCT execution traces.

These files are operational outputs and can grow quickly.
