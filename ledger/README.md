# Ledger Data

Persistent JSONL history of DDNA execution records.

## Contents
- `ddna_ledger.jsonl` — active append-only execution ledger.
- `ledger_pre_mutation.jsonl` — historical snapshot/reference ledger.

## Interlinking
- Written by `engine/ledger/append.py`.
- Can feed trend analysis, anomaly detection, and compliance checks.
