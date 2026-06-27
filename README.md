# Digital-DNA

**Deterministic structural genome verification for repositories changed by humans, agents, or recursive tooling.**

Digital-DNA verifies whether a repository still preserves its intended structural identity after edits. It extracts a repository genome, compares topology and dependency drift against baselines, computes retention, and emits a stability score that can be used as a local or CI gate.

```text
repository -> structural genome -> drift scan -> stability score -> ledger/report
```

## Why It Exists

Agent-modified repositories need more than tests. Tests answer whether selected behavior still works. Digital-DNA asks a different question:

> Did this repository retain the structure that makes it the same system?

That makes DDNA useful for:

- agent-code review pipelines,
- recursive evolution loops,
- specification-driven repositories,
- structural drift detection,
- CI gates that protect repository shape.

## Core Model

DDNA computes stability through retention minus bounded drift:

```text
drift_raw = (w_topology * drift_topology) + (w_dependency * drift_dependency)
drift = clamp(drift_raw, 0, 1)
stability = retention - drift
```

The invariant is enforced by runtime validation and tests.

## Install

```powershell
git clone https://github.com/jacksonjp0311-gif/Digital-DNA.git
cd Digital-DNA
python -m pip install -e .[dev]
```

## Quick Start

Run a scan:

```powershell
ddna scan
```

Return JSON:

```powershell
ddna scan --format json
```

Run a CI-style gate:

```powershell
ddna gate --min-stability 0.85
```

Render a report from the latest run:

```powershell
ddna report --format html --output artifacts/ddna-report.html
```

Rebuild baselines intentionally:

```powershell
ddna baseline --yes
```

## CLI

| Command | Purpose |
| --- | --- |
| `ddna scan` | Runs genome extraction, drift scoring, retention scoring, and writes `artifacts/last_run.json` by default. |
| `ddna scan --no-write` | Runs the same scan without updating the latest artifact. |
| `ddna gate --min-stability 0.85` | Returns non-zero when stability falls below the threshold. |
| `ddna baseline --yes` | Rebuilds genome, topology, and dependency baselines. |
| `ddna report` | Renders JSON, Markdown, or HTML from a scan record. |

The legacy entrypoint remains supported:

```powershell
python -m engine.orchestrator.run_ddna
```

## Repository Contract

Digital-DNA treats the repository as a structural organism with a measurable genome.

| Surface | Role |
| --- | --- |
| `engine/genome/` | Extracts normalized structural file genome. |
| `engine/drift/` | Computes topology and dependency drift. |
| `engine/stability/` | Computes retention and stability law. |
| `engine/orchestrator/` | Runs the canonical scan pipeline. |
| `engine/cli.py` | Provides the public `ddna` command. |
| `state/genomes/` | Stores genome baseline. |
| `state/environments/` | Stores topology and dependency baselines. |
| `artifacts/` | Stores latest run and rendered reports. |
| `tests/` | Locks runtime and invariant behavior. |

## Folder Mini-README System

Top-level scopes include local `README.md` files. Treat them as local contracts before editing a folder.

Human workflow:

1. Open the folder you intend to modify.
2. Read that folder's `README.md`.
3. Follow the mini-directory and sequencing notes.

Agent workflow:

1. Use the local `README.md` as the scope contract.
2. Preserve deterministic execution order and truth-surface invariants.
3. Avoid creating shadow pipelines that bypass the orchestrator.

## Baseline Policy

Baselines are allowed to initialize automatically in exploratory mode. CI or locked runs can require pre-existing baselines:

```powershell
$env:DDNA_BASELINE_LOCK = "1"
ddna scan
```

With `DDNA_BASELINE_LOCK=1`, missing baselines fail instead of silently initializing.

## Reports

Scan records include:

- `retention`
- `drift`
- `drift_raw`
- `drift_topology`
- `drift_dependency`
- `weights`
- `stability`
- `timestamp`

Render a shareable HTML report:

```powershell
ddna report --format html --output artifacts/ddna-report.html
```

## Development

```powershell
python -m pip install -e .[dev]
python -m pytest
ddna scan --format json
ddna gate --min-stability 0.0 --format json
ddna report --format markdown
```

## Release Gate

Before publishing a release:

```powershell
python -m pip install -e .[dev]
python -m pytest
ddna scan --format json
ddna gate --min-stability 0.0 --format json
ddna report --format html --output artifacts/ddna-report.html
python -m tools.ddna_loop --iterations 1
```

## Theory

Canonical theory documents live under `theory/`:

- `theory/digital_dna_software_theory_v1_3.tex`
- `theory/codex_digital_dna_theory_memory_architecture_v1_6.tex`
- `theory/README.md`

The reusable engineering theory is:

- preserve structural genome,
- measure topology and dependency drift,
- compute retention,
- keep stability auditable,
- gate changes when structure falls below tolerance.

## Non-Claim Lock

Digital-DNA does not prove semantic correctness, runtime safety, agent alignment, production readiness, or biological equivalence. It measures repository structural continuity under explicitly defined baselines and drift channels.
