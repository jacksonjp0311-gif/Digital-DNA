# Engine Overview

The `engine/` package is the execution core for Digital DNA (DDNA).

## Mini Directory
- `orchestrator/run_ddna.py` — canonical DDNA pipeline entrypoint.
- `drift/` — topology/dependency drift extraction and metrics.
- `genome/` — structural extraction/fingerprint utilities.
- `stability/` — retention and stability-law computation.
- `ledger/` — append/verify ledger primitives.
- `evolution/`, `mutations/`, `research/`, `episodic/`, `interface/` — advanced runtime subsystems.

## Sequence of Events
1. Orchestrator loads current structure and baselines.
2. Drift channels are computed and weighted.
3. Retention is computed and stability law enforced.
4. Record is validated and emitted to artifacts/ledger surfaces.

## Interlinking Notes
- `orchestrator/run_ddna.py` is the intended deterministic run entrypoint.
- `tools/ddna_loop.py` is the intended canonical loop entrypoint for repeated runs.
- Subsystems must preserve stability invariants and artifact contract shape.
