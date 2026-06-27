from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROLE_ALPHABET = {
    "runtime": "A",
    "validation": "C",
    "knowledge": "G",
    "state": "U",
}

DENY_DIRS = {
    ".git",
    ".github",
    ".pytest_cache",
    "__pycache__",
    "artifacts",
    "logs",
    "memory",
    "core_runtime",
    "ecosystem",
    "population",
    "organisms",
    "_backups",
    "_mutations",
    "_patch_backups",
}

INCLUDE_SUFFIXES = {".py", ".md", ".json", ".toml", ".yml", ".yaml", ".tex"}


def collect_signature_files(root: str | Path) -> list[str]:
    root_path = Path(root).resolve()
    files: list[str] = []
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root_path)
        parts = tuple(part.lower() for part in rel.parts)
        if any(part in DENY_DIRS or part.startswith("_backup") for part in parts):
            continue
        if path.suffix.lower() not in INCLUDE_SUFFIXES and path.name.lower() != "readme.md":
            continue
        files.append(rel.as_posix())
    return sorted(files)


def compute_bio_signature(files: Iterable[str], *, k: int = 3) -> dict[str, Any]:
    normalized = sorted({str(path).replace("\\", "/") for path in files})
    sequence = "".join(_role_base(path) for path in normalized)
    kmer_counts = _kmer_counts(sequence, k)
    contigs = _contig_lengths(normalized)
    motif_counts = _motif_counts(normalized)
    entropy = _shannon_entropy(sequence)
    max_entropy = math.log2(len(ROLE_ALPHABET)) if ROLE_ALPHABET else 1.0
    normalized_entropy = entropy / max_entropy if max_entropy else 0.0
    return {
        "alphabet": "ACGU",
        "sequence_length": len(sequence),
        "role_counts": dict(sorted(Counter(sequence).items())),
        "gc_like_content": _gc_like_content(sequence),
        "k": k,
        "distinct_kmers": len(kmer_counts),
        "kmer_entropy": _kmer_entropy(kmer_counts),
        "sequence_entropy": entropy,
        "normalized_sequence_entropy": normalized_entropy,
        "contig_count": len(contigs),
        "n50": _n50(contigs),
        "motifs": motif_counts,
        "fold_balance": _fold_balance(sequence),
    }


def _role_base(path: str) -> str:
    first = path.split("/", 1)[0].lower()
    suffix = Path(path).suffix.lower()
    if first in {"engine", "tools", "core_runtime"} or path.lower() == "run.py":
        return ROLE_ALPHABET["runtime"]
    if first == "tests" or suffix in {".schema.json"}:
        return ROLE_ALPHABET["validation"]
    if first in {"docs", "theory", "readme.md", "config", "schema"} or suffix in {".md", ".tex"}:
        return ROLE_ALPHABET["knowledge"]
    return ROLE_ALPHABET["state"]


def _gc_like_content(sequence: str) -> float:
    if not sequence:
        return 0.0
    return (sequence.count("G") + sequence.count("C")) / len(sequence)


def _kmer_counts(sequence: str, k: int) -> Counter[str]:
    if k < 1 or len(sequence) < k:
        return Counter()
    return Counter(sequence[index : index + k] for index in range(len(sequence) - k + 1))


def _kmer_entropy(counts: Counter[str]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def _shannon_entropy(sequence: str) -> float:
    if not sequence:
        return 0.0
    counts = Counter(sequence)
    total = len(sequence)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def _contig_lengths(files: list[str]) -> list[int]:
    by_top_level: dict[str, int] = {}
    for path in files:
        top_level = path.split("/", 1)[0]
        by_top_level[top_level] = by_top_level.get(top_level, 0) + 1
    return sorted(by_top_level.values(), reverse=True)


def _n50(lengths: list[int]) -> int:
    if not lengths:
        return 0
    half = sum(lengths) / 2
    running = 0
    for length in sorted(lengths, reverse=True):
        running += length
        if running >= half:
            return int(length)
    return int(lengths[-1])


def _motif_counts(files: list[str]) -> dict[str, int]:
    motifs = {
        "engine_runtime": 0,
        "tests_validation": 0,
        "docs_knowledge": 0,
        "config_policy": 0,
        "schema_contract": 0,
    }
    for path in files:
        lowered = path.lower()
        if lowered.startswith("engine/"):
            motifs["engine_runtime"] += 1
        if lowered.startswith("tests/"):
            motifs["tests_validation"] += 1
        if lowered.startswith("docs/") or lowered.startswith("theory/") or lowered.endswith(".md"):
            motifs["docs_knowledge"] += 1
        if lowered.startswith("config/"):
            motifs["config_policy"] += 1
        if lowered.startswith("schema/") or lowered.endswith(".schema.json"):
            motifs["schema_contract"] += 1
    return motifs


def _fold_balance(sequence: str) -> float:
    if not sequence:
        return 0.0
    pairs = min(sequence.count("A"), sequence.count("U")) + min(sequence.count("C"), sequence.count("G"))
    return pairs / len(sequence)
