# CODEX CONTRACTS (Digital-DNA)
These are machine-facing contracts for Code GPT.

## Locked invariants
- Do not change metric definitions without version bump + migration note.
- Ledger files are append-only.
- Baselines in /state are treated as read-only reference truth unless explicitly requested.

## Canon outputs
- artifacts/last_run.json is the authoritative latest-run snapshot.
- ledger/ddna_ledger.jsonl is append-only run history.
- docs/feedback/packet_latest.json is the Codex ingest capsule (always overwritten).
