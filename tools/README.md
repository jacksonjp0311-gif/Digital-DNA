# Tools Overview

The `tools/` folder contains utility scripts for local loop automation.

## Mini Directory
- `ddna_loop.py` — canonical DDNA loop entrypoint (single-run or continuous).

## Sequence of Events
1. Tool runs `engine.orchestrator.run_ddna` via module entrypoint.
2. Snapshot/replay/feedback artifacts are updated deterministically.
3. Optional iteration scheduling (`--iterations` / `--forever`) controls loop cadence.

## Interlinking Notes
- Run from repo root for deterministic relative-path behavior.
- Preferred loop command: `python -m tools.ddna_loop`.
- Legacy wrappers (`boot_ddna.py`, `engine/evolution_loop.py`) delegate here for compatibility.
