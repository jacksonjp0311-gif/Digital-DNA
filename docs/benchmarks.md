# Digital-DNA Benchmarks

Run date: 2026-06-27  
Environment: Windows, Python 3.12, local editable install

## Validation

| Command | Result |
| --- | --- |
| `python -m pytest` | 8 passed |
| `ddna scan --format json` | PASS |
| `ddna gate --format json` | PASS |
| `ddna explain --format markdown` | PASS |
| `ddna signature --format json` | PASS |
| `ddna report --format html --output artifacts/ddna-report.html` | PASS |

## Structural Metrics

| Metric | Value |
| --- | ---: |
| stability | 0.8092440801457195 |
| retention | 1.0 |
| drift | 0.19075591985428053 |
| drift_topology | 0.06944444444444445 |
| drift_dependency | 0.12131147540983607 |

## Bio-Signature Metrics

| Metric | Value |
| --- | ---: |
| sequence_length | 286 |
| contig_count | 27 |
| n50 | 74 |
| gc_like_content | 0.22377622377622378 |
| distinct_kmers | 21 |
| kmer_entropy | 2.437346645958553 |
| normalized_sequence_entropy | 0.8120428667532061 |
| fold_balance | 0.3041958041958042 |

## Motifs

| Motif | Count |
| --- | ---: |
| engine_runtime | 74 |
| tests_validation | 9 |
| docs_knowledge | 58 |
| config_policy | 6 |
| schema_contract | 1 |
