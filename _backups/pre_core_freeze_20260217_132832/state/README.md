# State Overview

The `state/` folder is the canonical persisted runtime state surface.

## Mini Directory
- `environments/` — topology/dependency baseline snapshots.
- `genomes/` — baseline genome state.
- `candidates/` — generated candidate runtime programs and metadata.
- `interface/` — stateful interface channels and progress.
- `research/` — queued research tasks and journals.
- `ddna_evolution_lineage.jsonl` — evolution lineage continuity stream.

## Sequence of Events
1. Baselines are loaded by orchestrator and drift channels.
2. Evolution/candidate flows emit candidate artifacts.
3. Interface/research subsystems append structured state updates.

## Interlinking Notes
- This folder defines truth for stateful continuity across runs.
- Baseline changes can alter test expectations and drift outcomes.
