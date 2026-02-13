# CODEX–EPISODIC INVARIANT MEMORY THEORY (EIMT) → DIGITAL-DNA INTEGRATION (v1.0)

Author: James Paul Jackson  
Date: February 2026  
Status: **EXECUTION-LEVEL INTEGRATION NOTE** (software-aligned; no ontology claims)

## 1) Purpose

Digital-DNA already computes an invariant of the form:

- drift_total = drift_topology + drift_dependency
- stability = retention - drift_total

But retention was previously a placeholder, and the system had no explicit
episodic operators (boundary gating, replay, consolidation). This note
installs EIMT as an **execution architecture** inside Digital-DNA.

## 2) Canonical mapping (EIMT → Digital-DNA)

Episode state:
- EIMT: E = (c, x, t, s)
- DDNA:
  - c (context) = hashed environment + config:
    - state/environments/topology_baseline.json
    - state/environments/dependency_baseline.json
    - config/weights.json + config/thresholds.json
  - x (content) = live observation:
    - extracted topology (.py paths)
    - extracted dependency edges (import graph)
    - genome fingerprint (repo structural signature)
  - t (time) = timestamp
  - s (self) = mode + git head + run metadata

Memory field:
- EIMT: M = {E1..EN}
- DDNA: artifacts/history/run_*.json (append-only episodes)

Ledger:
- EIMT: L_{k+1} = L_k ⊕ ℓ_k
- DDNA: docs/ledger/docs_ledger.jsonl (append-only)

## 3) Operators installed

### (A) Context binding
Compute a stable context_hash over baseline+config (UTF-8 no-BOM).
This prevents context corruption from silently destabilizing retrieval.
(Observed failure mode: UTF-8 BOM crash.)

### (B) Contractive retrieval (software form)
- Drift remains bounded and validated.
- Baseline lock mode can forbid auto-init:
  - DDNA_BASELINE_LOCK=1 → missing baselines are errors.

### (C) Replay stabilization
Compute rtifacts/replay_k.json over last K episodes:
- mean stability, last stability, delta, slope, min/max
This is the **explicit replay operator**.

### (D) Consolidation
Two-timescale persistence:
- FAST: artifacts/last_run.json (overwrite)
- SLOW: docs/ledger/docs_ledger.jsonl (append-only)
Replay summary bridges fast → slow.

### (E) Event boundary gating
Compute:
- boundary_score ∈ [0,1]
- boundary_event = boundary_score > Bcrit
Bcrit is read from config/thresholds.json (default 0.5).

Boundary score includes:
- context_hash change (baseline/config changed)
- repo_hash change (git head changed)
- optional drift cue

## 4) Stability invariant (DDNA)
We lock:
- stability = retention - drift_total
where:
- retention = genome similarity to stored baseline genome (0..1)
- drift_total = drift_topology + drift_dependency (0..∞; expected small)

## 5) Artifacts (authoritative outputs)
- artifacts/last_run.json (overwrite)
- artifacts/replay_k.json (overwrite)
- artifacts/history/run_YYYYMMDD_HHMMSS.json (append-only)
- docs/feedback/packet_latest.json (overwrite)
- docs/feedback/packets/packet_YYYYMMDD_HHMMSS.json (append-only)
- docs/ledger/docs_ledger.jsonl (append-only)

## 6) Non-claims
This is **software architecture** and invariant accounting. It does not claim:
- neuroscience truth,
- cognition,
- phenomenology,
- training effects.

It is an execution-stability framework usable across domains.