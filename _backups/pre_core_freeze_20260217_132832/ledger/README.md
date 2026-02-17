# Ledger Overview

The `ledger/` folder is the primary append-only continuity stream for DDNA runs.

## Mini Directory
- `ddna_ledger.jsonl` — main run ledger.
- `ledger_pre_mutation.jsonl` — pre-mutation continuity trail.

## Sequence of Events
1. Runtime emits validated records.
2. Records append to ledger streams for auditability.
3. Downstream analysis consumes ledger history.

## Interlinking Notes
- Ledger files are append-only truth surfaces.
- Keep schema consistency with `engine/ledger/` helpers.
