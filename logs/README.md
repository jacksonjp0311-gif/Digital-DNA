# Logs Overview

The `logs/` folder stores operational telemetry, progress logs, and crash traces.

## Mini Directory
- `boot_log.txt`, `last_traceback.txt` — startup and failure context.
- `*.jsonl` files — evolution/progress/mutation/runtime streams.
- `evolution/` — dedicated self-write and crash-ledger logging.

## Sequence of Events
1. Runtime and evolution flows emit log events.
2. Crash/boot traces are persisted for recovery.
3. Analysis tooling reads logs to diagnose drift and instability.

## Interlinking Notes
- Generated operational output; prune/archive intentionally.
- Use logs with ledger/state for full continuity context.
