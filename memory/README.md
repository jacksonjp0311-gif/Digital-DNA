# Memory Overview

The `memory/` folder stores tiny runtime continuity markers and flags.

## Mini Directory
- `phase7_enabled.txt` — phase gate/marker used by runtime flows.

## Sequence of Events
1. Runtime checks marker files for enabled capabilities.
2. Evolution/boot flows condition behavior on those flags.

## Interlinking Notes
- Treat as stateful control markers.
- Keep values simple and deterministic.
