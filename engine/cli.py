from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engine.drift.dependency_graph import extract_dependency_graph, save_baseline as save_dependency_baseline
from engine.drift.topology import extract_topology, save_baseline as save_topology_baseline
from engine.genome.extract import extract_genome
from engine.orchestrator.run_ddna import ARTIFACT_PATH, BASELINE_PATH, ROOT, _write_json, run_scan
from engine.reporting import load_record, render_html, render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ddna",
        description="Digital-DNA structural genome scanner and drift gate.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Run a structural scan.")
    scan.add_argument("--format", choices=("json", "markdown"), default="markdown")
    scan.add_argument("--output", type=Path, default=None)
    scan.add_argument("--no-write", action="store_true", help="Do not update artifacts/last_run.json.")

    gate = sub.add_parser("gate", help="Fail when stability falls below a threshold.")
    gate.add_argument("--min-stability", type=float, default=0.85)
    gate.add_argument("--format", choices=("json", "markdown"), default="markdown")

    baseline = sub.add_parser("baseline", help="Rebuild genome, topology, and dependency baselines.")
    baseline.add_argument("--yes", action="store_true", help="Confirm baseline rewrite.")

    report = sub.add_parser("report", help="Render a report from a scan record.")
    report.add_argument("--input", type=Path, default=ARTIFACT_PATH)
    report.add_argument("--format", choices=("json", "markdown", "html"), default="markdown")
    report.add_argument("--output", type=Path, default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "scan":
            record = run_scan(write_artifact=not args.no_write)
            _emit_record(record, args.format, args.output)
            return 0

        if args.command == "gate":
            record = run_scan(write_artifact=True)
            _emit_record(record, args.format, None)
            return 0 if float(record["stability"]) >= args.min_stability else 2

        if args.command == "baseline":
            if not args.yes:
                raise ValueError("baseline rewrite requires --yes")
            genome = extract_genome(ROOT)
            _write_json(BASELINE_PATH, {"files": list(genome.get("files", []))})
            save_topology_baseline(extract_topology())
            save_dependency_baseline(extract_dependency_graph())
            print(json.dumps({"status": "baseline_rebuilt", "root": str(ROOT)}, indent=2))
            return 0

        if args.command == "report":
            record = load_record(args.input)
            _emit_record(record, args.format, args.output)
            return 0

        return 1
    except Exception as exc:  # noqa: BLE001 - CLI should emit clean operator errors.
        print(f"ddna: {exc}", file=sys.stderr)
        return 1


def _emit_record(record: dict[str, object], fmt: str, output: Path | None) -> None:
    if fmt == "json":
        text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    elif fmt == "html":
        text = render_html(record)
    else:
        text = render_markdown(record)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    raise SystemExit(main())
