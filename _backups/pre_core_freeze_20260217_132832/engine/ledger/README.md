# Ledger Engine

The ledger engine provides run-history persistence.

## Mini Directory
- `append.py` — appends one JSON record per line to the ledger file.
- `verify.py` — placeholder for continuity verification.

## How It Works
- Appends immutable JSONL entries after each orchestrator run.
- Enables auditability and trend analysis across runs.

## Interlinking
- Called by `engine/orchestrator/run_ddna.py`.
- Writes to `ledger/ddna_ledger.jsonl`.
