# Orchestrator

The orchestrator is the runtime entrypoint for DDNA execution.

## Mini Directory
- `run_ddna.py` — full pipeline orchestration and artifact/ledger generation.

## Sequence of Events
1. Load current genome.
2. Load/init baseline genome.
3. Compute retention.
4. Compute topology and dependency drift channels.
5. Load channel weights and clamp drift.
6. Compute stability.
7. Append ledger and write `artifacts/last_run.json`.

## Interlinking
- Coordinates all engine packages.
- Reads `config/weights.json`.
- Writes `ledger/ddna_ledger.jsonl` and `artifacts/last_run.json`.
