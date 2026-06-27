# Digital-DNA

**Structural genome intelligence for repositories changed by humans, agents, or recursive tooling.**

Digital-DNA verifies whether a repository still preserves its intended structural identity after edits. It extracts a repository genome, compares topology and dependency drift against baselines, computes retention, emits a policy-gated stability score, and now produces a genome-inspired bio-signature for repository composition.

```text
repository -> structural genome -> bio-signature -> drift scan -> policy gate -> report
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

## What It Measures

| Layer | Question |
| --- | --- |
| Structural genome | Which files define the system's preserved identity? |
| Topology drift | Did the file topology move outside the baseline envelope? |
| Dependency drift | Did import/dependency relationships change unexpectedly? |
| Retention | How much of the baseline structure remains intact? |
| Bio-signature | What is the repo's role composition, entropy, motifs, and contiguity? |
| Policy gate | Does the current structure pass the configured continuity contract? |

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
ddna gate
```

Explain the latest gate decision:

```powershell
ddna explain
```

Print the repository bio-signature:

```powershell
ddna signature
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
| `ddna gate` | Returns non-zero when the scan violates `config/policy.json`. |
| `ddna explain` | Explains the latest gate decision and violated constraints. |
| `ddna signature` | Computes the genome-inspired repository signature. |
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

## Gate Policy

The default structural continuity policy lives at `config/policy.json`:

```json
{
  "min_stability": 0.8,
  "max_drift": 0.2,
  "max_topology_drift": 0.12,
  "max_dependency_drift": 0.15,
  "require_retention": 0.95
}
```

Override the stability floor for one run:

```powershell
ddna gate --min-stability 0.9
```

## Bio-Signature

Digital-DNA maps repository file roles into a deterministic `ACGU` alphabet:

| Base | Repository role |
| --- | --- |
| `A` | Runtime and engine code |
| `C` | Validation, tests, and contracts |
| `G` | Knowledge, docs, schemas, and policy |
| `U` | State, artifacts, and uncategorized support files |

The signature reports:

- `gc_like_content`: validation/knowledge density, inspired by GC content.
- `kmer_entropy`: short-window role diversity, inspired by k-mer composition.
- `normalized_sequence_entropy`: role-distribution complexity.
- `n50`: repository contiguity across top-level structural groups.
- `motifs`: conserved repo features such as runtime, tests, docs, config, and schema.
- `fold_balance`: an RNA-inspired complement-balance proxy over `A/U` and `C/G` roles.

This is an engineering analogy, not a biological claim. The purpose is to make repository structure measurable, comparable, and explainable.

## Reports

Scan records include:

- `retention`
- `drift`
- `drift_raw`
- `drift_topology`
- `drift_dependency`
- `weights`
- `stability`
- `bio_signature`
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
ddna gate --format json
ddna explain
ddna signature --format json
ddna report --format markdown
```

## Release Gate

Before publishing a release:

```powershell
python -m pip install -e .[dev]
python -m pytest
ddna scan --format json
ddna gate --format json
ddna explain
ddna signature --format json
ddna report --format html --output artifacts/ddna-report.html
python -m tools.ddna_loop --iterations 1
```

## Current Benchmarks

Local benchmark run on Windows, Python 3.12, from this repository:

| Command | Result |
| --- | --- |
| `python -m pytest` | 8 tests passed |
| `ddna scan --format json` | PASS, stability `0.8092440801457195` |
| `ddna gate --format json` | PASS under `config/policy.json` |
| `ddna signature --format json` | PASS, emits role composition, entropy, N50, motifs, and fold balance |
| `ddna report --format html` | PASS, renders shareable structural report |

Full benchmark notes: `docs/benchmarks.md`.

Research mapping: `docs/research_mapping.md`.

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
