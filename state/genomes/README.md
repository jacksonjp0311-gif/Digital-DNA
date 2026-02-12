# Genome Baselines

Stores baseline genome signatures for retention computations.

## Contents
- `baseline.json` — sorted hash list of baseline Python source signatures.

## Interlinking
- Loaded by `engine/orchestrator/run_ddna.py`.
- Compared against newly extracted genome from `engine/genome/extract.py`.
