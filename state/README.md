# State

State stores persistent baselines used for deterministic comparisons.

## Mini Directory
- `genomes/` — baseline genome signatures.
- `environments/` — topology/dependency drift baselines.

## Interlinking
- Read and written by `engine/genome` and `engine/drift` modules.
- Controls drift/retention behavior across successive runs.
