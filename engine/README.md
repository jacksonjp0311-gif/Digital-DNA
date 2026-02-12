# Engine Overview

The `engine/` package is the execution core for Digital DNA (DDNA).

## Mini Directory
- `genome/` — hashes Python source files into a deterministic genome signature set.
- `drift/` — computes drift channels from topology and import dependency changes.
- `stability/` — computes retention and final stability law (`S = C - D`).
- `ledger/` — appends immutable run records.
- `orchestrator/` — wires all modules together and produces the run artifact.

## Sequence of Events
1. `orchestrator/run_ddna.py` extracts current genome signatures.
2. Baseline genome is loaded (or initialized) from `state/genomes/baseline.json`.
3. Retention (`C`) is computed using genome overlap.
4. Topology and dependency graphs are extracted and drift channels computed.
5. Drift is weighted, clamped to `[0, 1]`, and used to compute stability (`S`).
6. Record is appended to ledger and written to `artifacts/last_run.json`.

## Interlinking Notes
- `orchestrator` is the only entrypoint and depends on all sub-engines.
- `drift` and `genome` consume repository structure directly.
- `state/` and `config/` drive deterministic behavior across runs.
