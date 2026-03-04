# Tools Overview

The `tools/` folder contains utility scripts for local loop automation.

## Mini Directory
- `ddna_loop.py` — canonical DDNA loop entrypoint (single-run or continuous).
- `rebaseline_structures.py` — rebuilds dependency/topology/genome baselines in one pass to keep drift metrics truthful.

## Sequence of Events
1. Tool runs `engine.orchestrator.run_ddna` via module entrypoint.
2. Snapshot/replay/feedback artifacts are updated deterministically.
3. Optional iteration scheduling (`--iterations` / `--forever`) controls loop cadence.

### Baseline Refresh Sequence
1. Run `python -m tools.rebaseline_structures` (or pass `--dependency/--topology/--genome` flags to target channels).
2. The script regenerates the normalized dependency graph, topology list, and genome file set using the latest filters.
3. Follow with `python -m engine.orchestrator.run_ddna` to verify `artifacts/last_run.json` reports `stability: 1.0`.

## Interlinking Notes
- Run from repo root for deterministic relative-path behavior.
- Preferred loop command: `python -m tools.ddna_loop`.
- Legacy wrappers (`boot_ddna.py`, `engine/evolution_loop.py`) delegate here for compatibility.
