# Configuration

Configuration files define DDNA runtime behavior and policy bounds.

## Mini Directory
- `weights.json` — drift channel weights (`topology`, `dependency`).
- `thresholds.json` — thresholds for policy layers/integration consumers.
- `environments.json` — environment configuration registry.

## Interlinking
- `engine/orchestrator/run_ddna.py` consumes `weights.json` directly.
- Other config files are ready for future policy/control-plane integrations.
