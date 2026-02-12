# Test Suite

Executable validation scripts for DDNA invariants and output contracts.

## Mini Directory
- `behavioral_test_v1.py` — validates required output keys and `S = C - D`.
- `structural_envelope_test_v1.py` — validates drift clamp envelope and emits proof.
- `results/` — persisted proof artifacts from test execution.

## Interlinking
- Tests invoke `engine.orchestrator.run_ddna` as a subprocess.
- Assertions are made against `artifacts/last_run.json` outputs.
