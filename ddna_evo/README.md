# DDNA Evo Overview

The `ddna_evo/` folder contains evolutionary runner logic used for mutation/evaluation experimentation.

## Mini Directory
- `run_evo.py` — entrypoint for iterative evolution experiments.

## Sequence of Events
1. Evolution runner initializes runtime/genome candidates.
2. Candidate programs are evaluated and scored.
3. Logs/state artifacts are emitted into `logs/` and `state/candidates/`.

## Interlinking Notes
- This path is experimental and should not bypass the canonical orchestrator contract.
- Use from repo root so relative paths resolve deterministically.
