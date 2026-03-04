from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.drift.dependency_graph import (
    extract_dependency_graph,
    save_baseline as save_dependency_baseline,
)
from engine.drift.topology import (
    extract_topology,
    save_baseline as save_topology_baseline,
)
from engine.genome.extract import extract_genome

ROOT = Path(__file__).resolve().parents[1]
GENOME_BASELINE_PATH = ROOT / "state" / "genomes" / "baseline.json"


def write_genome_baseline(files: list[str]) -> None:
    payload = {"files": sorted({*files})}
    GENOME_BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GENOME_BASELINE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def rebaseline(topology: bool, dependency: bool, genome: bool) -> None:
    if dependency:
        dep_graph = extract_dependency_graph()
        save_dependency_baseline(dep_graph)
        print(f"Dependency baseline updated -> {len(dep_graph)} edges")

    if topology:
        topo = extract_topology()
        save_topology_baseline(topo)
        print(f"Topology baseline updated -> {len(topo)} files")

    if genome:
        genome_files = extract_genome(ROOT).get("files", [])
        write_genome_baseline(genome_files)
        print(f"Genome baseline updated -> {len(genome_files)} files")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild DDNA structural baselines")
    parser.add_argument(
        "--topology",
        action="store_true",
        help="Regenerate topology baseline",
    )
    parser.add_argument(
        "--dependency",
        action="store_true",
        help="Regenerate dependency baseline",
    )
    parser.add_argument(
        "--genome",
        action="store_true",
        help="Regenerate genome baseline",
    )

    args = parser.parse_args()
    targets = {
        "topology": args.topology,
        "dependency": args.dependency,
        "genome": args.genome,
    }

    if not any(targets.values()):
        targets = {k: True for k in targets}

    rebaseline(
        topology=targets["topology"],
        dependency=targets["dependency"],
        genome=targets["genome"],
    )


if __name__ == "__main__":
    main()
