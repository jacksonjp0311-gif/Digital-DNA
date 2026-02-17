# Config Overview

The `config/` folder contains runtime coefficients and invariant policy inputs.

## Mini Directory
- `weights.json` — topology/dependency drift channel weights.
- `thresholds.json` — threshold tuning and criterion values used by runtime flows.
- `goals.json` — high-level objective/config targets.
- `environments.json` — environment descriptors used by execution tooling.

## Sequence of Events
1. Orchestrator loads weights and validates constraints.
2. Runtime/evolution loops consume thresholds and goal parameters.
3. Config values influence drift weighting and decision boundaries.

## Interlinking Notes
- Config data is part of deterministic behavior; keep JSON valid and explicit.
- Changes here can invalidate baseline expectations in `state/` and tests.
