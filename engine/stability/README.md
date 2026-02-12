# Stability Engine

The stability engine implements DDNA's primary invariant.

## Mini Directory
- `retention.py` — retention ratio (`common / baseline`).
- `compute_S.py` — stability law (`S = C - D`).

## How It Works
- Retention (`C`) comes from genome overlap.
- Drift (`D`) comes from weighted topology/dependency channels.
- Stability is deterministic and directly test-verified.

## Interlinking
- Inputs come from `engine/genome` and `engine/drift`.
- Outputs are emitted by `engine/orchestrator` and validated by tests.
