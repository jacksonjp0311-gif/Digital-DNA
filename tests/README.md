# Tests Overview

The `tests/` folder validates DDNA invariants and artifact contracts.

## Mini Directory
- `behavioral_test_v1.py` — checks required run artifact keys and stability law.
- `structural_envelope_test_v1.py` — validates drift envelope/clamp invariants.
- `hardening_test_v2.py` — validates baseline lock and contract hardening behavior.
- `results/` — emitted proof artifacts.

## Sequence of Events
1. Tests run orchestrator via module entrypoint.
2. `artifacts/last_run.json` is read and validated.
3. Optional proof artifacts are emitted under `tests/results/`.

## Interlinking Notes
- Tests assume orchestrator contract shape is stable.
- Avoid changing artifact schema without coordinated test updates.
