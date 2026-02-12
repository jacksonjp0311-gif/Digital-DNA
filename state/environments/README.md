# Environment Baselines

Stores baseline structures used by drift channels.

## Contents
- `topology_baseline.json` — baseline Python file topology.
- `dependency_baseline.json` — baseline import-edge graph.

## Interlinking
- Used by `engine/drift/topology.py` and `engine/drift/dependency_graph.py`.
- Enables channel-level drift deltas across runs.
