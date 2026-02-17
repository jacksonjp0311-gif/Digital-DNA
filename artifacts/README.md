# Artifacts Overview

The `artifacts/` folder stores deterministic runtime outputs emitted by orchestrated DDNA runs.

## Mini Directory
- `last_run.json` — canonical run artifact consumed by tests and continuity tooling.

## Sequence of Events
1. `engine/orchestrator/run_ddna.py` computes retention, drift channels, and stability.
2. The validated record is written to `artifacts/last_run.json`.
3. Tests read this artifact as the truth surface.

## Interlinking Notes
- Treat this folder as generated output, not authored source.
- Regenerate artifacts by running the orchestrator, not by hand editing.
