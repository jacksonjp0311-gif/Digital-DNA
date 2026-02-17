# Genome Overview

The `genome/` folder stores runtime genome payloads/spec artifacts.

## Mini Directory
- `genome_spec.json` — active genome specification snapshot.
- `best_genome.json` — best-known genome/candidate state.

## Sequence of Events
1. Genome specs are loaded by runtime/evolution paths.
2. Candidate updates may produce new best genome artifacts.
3. Outputs are persisted for continuity and replay.

## Interlinking Notes
- Coordinate with `engine/genome/` code paths and `state/genomes/` baselines.
- Treat as state artifacts, not core source modules.
