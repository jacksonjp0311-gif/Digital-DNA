# Tools Overview

The `tools/` folder contains utility scripts for local loop automation.

## Mini Directory
- `ddna_loop.py` — local helper for repeated DDNA run cycles.

## Sequence of Events
1. Tool initializes loop inputs.
2. Orchestrator is executed repeatedly.
3. Outputs are observed through artifacts/logs/ledger.

## Interlinking Notes
- Run from repo root for deterministic relative-path behavior.
- Tools should call canonical engine entrypoints instead of duplicating logic.
