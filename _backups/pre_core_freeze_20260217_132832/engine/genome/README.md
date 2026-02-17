# Genome Engine

The genome engine captures a structural fingerprint of Python code.

## Mini Directory
- `extract.py` — walks project files and SHA-256 hashes each `.py` file.
- `compare.py` — calculates intersection size between baseline and current genomes.
- `normalize.py` — utility normalizer (currently not used by orchestrator).

## How It Works
- A genome is represented as sorted SHA-256 hashes.
- Retention quality is derived from overlap between baseline hashes and current hashes.

## Interlinking
- Called by `engine/orchestrator/run_ddna.py`.
- Baseline storage is in `state/genomes/baseline.json`.
