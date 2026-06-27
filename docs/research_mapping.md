# Research Mapping

Digital-DNA borrows measurement patterns from genomics and RNA analysis as engineering analogies for repository structure. It does not claim that software repositories are biological organisms.

## Translated Concepts

| Biology / bioinformatics concept | Digital-DNA implementation |
| --- | --- |
| GC content | `gc_like_content`, the proportion of validation/knowledge bases (`C` and `G`) in the repository role sequence. |
| k-mer analysis | `distinct_kmers` and `kmer_entropy` over fixed-length role windows. |
| Sequence entropy / surprisal | `sequence_entropy` and `normalized_sequence_entropy` over the role alphabet. |
| Assembly contiguity / N50 | `n50` over top-level repository structural groups. |
| Conserved motifs | Counts for runtime, tests, docs, config, and schema motifs. |
| RNA complement balance | `fold_balance`, a lightweight role-pairing proxy across `A/U` and `C/G`. |

## Source Grounding

- QUAST and genome assembly QC use metrics such as GC content and N50-style contiguity to summarize assemblies.
- k-mer methods count short subsequences and are widely used for composition, comparison, and alignment-free genome analysis.
- Information-theoretic sequence measures such as entropy and surprisal can describe local sequence information without requiring alignment.
- RNA structure workflows often use energy or balance ideas to reason about structural stability; Digital-DNA uses only a bounded analogy, not thermodynamic prediction.
- Software evolution research has used entropy and dependency/topology graphs to reason about change, complexity, and structural degradation.

## Boundary

The `bio_signature` field is a repository composition signature. It is useful for comparing structural states across releases, but it is not a biological model and does not prove semantic correctness.
