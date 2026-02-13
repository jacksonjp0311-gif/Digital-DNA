# CODEX SYSTEM PROMPT (Repo-local)
You are operating inside Digital-DNA. Maintain determinism and coherence.

## Allowed edits
- engine/* (implementation)
- docs/codex/* (contracts + runbooks)
- docs/feedback/* (packets, templates, iteration notes)

## Forbidden edits (unless explicitly authorized)
- state/** baselines (genomes/environments)
- rewriting theory/*.tex unless requested
- deleting ledger history

## Required behaviors
- Preserve invariants and report any attempted metric mutation.
- Prefer additive changes with explicit version stamps.
- Every change must update docs/feedback/packet_latest.json expectations if behavior changes.
