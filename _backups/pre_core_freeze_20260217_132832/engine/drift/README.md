# Drift Engine

The drift engine measures structural movement across two channels.

## Mini Directory
- `topology.py` — computes drift from Python file path set differences.
- `dependency_graph.py` — computes drift from import graph edge differences.
- `artifact.py`, `dependency.py`, `interface.py` — placeholder channel stubs.

## How It Works
- For each channel, a baseline is loaded from `state/environments/`.
- Drift is `|symmetric_difference(current, baseline)| / |baseline|`.
- Channels are weighted in orchestrator (`config/weights.json`) and clamped.

## Interlinking
- `orchestrator` calls both active drift channels.
- Drift outputs feed `engine/stability` for final law computation.
