# Developer Overview

The `developer/` folder contains maintenance utilities, snapshots, reports, and internal diagnostics.

## Mini Directory
- `module_*.py` — analysis helpers for health/drift and structure mapping.
- `module_*.json` — generated module inventories and metrics.
- `README_*.md` — component explainers.
- `reports/`, `snapshots/`, `backup/`, `tmp/` — diagnostics and historical recovery material.

## Sequence of Events
1. Developer scripts scan project structure and runtime outputs.
2. Reports and snapshots are generated for review.
3. Findings inform cleanup, documentation, and repair actions.

## Interlinking Notes
- This directory is support tooling; production runtime lives under `engine/`.
- Prefer reproducible scripts over manual edits for generated diagnostics.
