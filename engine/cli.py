from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engine.drift.dependency_graph import extract_dependency_graph, save_baseline as save_dependency_baseline
from engine.drift.topology import extract_topology, save_baseline as save_topology_baseline
from engine.bio_signature import collect_signature_files, compute_bio_signature
from engine.genome.extract import extract_genome
from engine.orchestrator.run_ddna import ARTIFACT_PATH, BASELINE_PATH, ROOT, _write_json, run_scan
from engine.policy import attach_gate, evaluate_gate, explain_record, load_policy
from engine.reporting import load_record, render_html, render_markdown

POLICY_PATH = ROOT / "config" / "policy.json"


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

    gate = sub.add_parser("gate", help="Fail when structural continuity violates policy.")
    gate.add_argument("--min-stability", type=float, default=None, help="Override policy min_stability.")
    gate.add_argument("--policy", type=Path, default=POLICY_PATH)
    gate.add_argument("--format", choices=("json", "markdown"), default="markdown")

    baseline = sub.add_parser("baseline", help="Rebuild genome, topology, and dependency baselines.")
    baseline.add_argument("--yes", action="store_true", help="Confirm baseline rewrite.")

    report = sub.add_parser("report", help="Render a report from a scan record.")
    report.add_argument("--input", type=Path, default=ARTIFACT_PATH)
    report.add_argument("--format", choices=("json", "markdown", "html"), default="markdown")
    report.add_argument("--output", type=Path, default=None)

    explain = sub.add_parser("explain", help="Explain the latest structural gate decision.")
    explain.add_argument("--input", type=Path, default=ARTIFACT_PATH)
    explain.add_argument("--policy", type=Path, default=POLICY_PATH)
    explain.add_argument("--format", choices=("json", "markdown"), default="markdown")

    signature = sub.add_parser("signature", help="Print the genome-inspired repository bio-signature.")
    signature.add_argument("--format", choices=("json", "markdown"), default="markdown")

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
            policy = load_policy(args.policy)
            if args.min_stability is not None:
                policy["min_stability"] = float(args.min_stability)
            gate_result = evaluate_gate(record, policy)
            _emit_record(attach_gate(record, gate_result), args.format, None)
            return 0 if gate_result.passed else 2

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

        if args.command == "explain":
            record = load_record(args.input)
            policy = load_policy(args.policy)
            gate_result = evaluate_gate(record, policy)
            if args.format == "json":
                print(json.dumps(attach_gate(record, gate_result), indent=2, sort_keys=True))
            else:
                print(explain_record(record, gate_result), end="")
            return 0 if gate_result.passed else 2

        if args.command == "signature":
            signature = compute_bio_signature(collect_signature_files(ROOT))
            if args.format == "json":
                print(json.dumps(signature, indent=2, sort_keys=True))
            else:
                print(_render_signature_markdown(signature), end="")
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


def _render_signature_markdown(signature: dict[str, object]) -> str:
    lines = [
        "# Digital-DNA Bio-Signature",
        "",
        f"**Alphabet:** `{signature['alphabet']}`",
        f"**Sequence length:** `{signature['sequence_length']}`",
        f"**GC-like content:** `{float(signature['gc_like_content']):.6f}`",
        f"**Normalized entropy:** `{float(signature['normalized_sequence_entropy']):.6f}`",
        f"**N50:** `{int(signature['n50'])}`",
        f"**Fold balance:** `{float(signature['fold_balance']):.6f}`",
        "",
        "## Motifs",
        "",
        "| Motif | Count |",
        "| --- | ---: |",
    ]
    for key, value in sorted(dict(signature["motifs"]).items()):
        lines.append(f"| `{key}` | {int(value)} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
