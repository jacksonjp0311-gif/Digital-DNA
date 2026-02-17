from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.episodic.context import read_thresholds
from engine.episodic.replay import write_replay_summary

ART = ROOT / "artifacts"
HIST = ART / "history"
LAST = ART / "last_run.json"
REPLAY = ART / "replay_k.json"

DOCS = ROOT / "docs"
FEEDBACK = DOCS / "feedback"
PACKETS = FEEDBACK / "packets"
DOCS_LEDGER = DOCS / "ledger" / "docs_ledger.jsonl"
PACKET_LATEST = FEEDBACK / "packet_latest.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs() -> None:
    for p in [ART, HIST, FEEDBACK, PACKETS, DOCS / "ledger"]:
        p.mkdir(parents=True, exist_ok=True)


def run_engine() -> None:
    subprocess.run(
        [sys.executable, "-m", "engine.orchestrator.run_ddna"],
        cwd=str(ROOT),
        check=True,
    )


def read_json(path: Path) -> dict[str, Any] | list[Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


def run_once() -> dict[str, Any]:
    ensure_dirs()
    thresholds = read_thresholds()
    replay_k = int(thresholds.get("replay_K", 10))

    run_engine()

    if not LAST.exists():
        raise RuntimeError("Engine did not produce artifacts/last_run.json")

    snap = read_json(LAST) or {}

    snap_path = HIST / f"run_{stamp()}.json"
    snap_path.write_text(json.dumps(snap, indent=2), encoding="utf-8")

    replay = write_replay_summary(replay_k)

    files = sorted(HIST.glob("run_*.json"))
    prev_stability = None
    curr_stability = float((snap or {}).get("stability", 0.0))
    delta = None
    if len(files) >= 2:
        prev = read_json(files[-2]) or {}
        prev_stability = float(prev.get("stability", 0.0))
        delta = curr_stability - prev_stability

    drift_value = snap.get("drift")

    packet = {
        "timestamp": now_iso(),
        "repo": "Digital-DNA",
        "mode": "PY_LOOP",
        "source_metrics": "artifacts/last_run.json",
        "episode": {
            "context_hash": snap.get("context_hash"),
            "repo_hash": snap.get("repo_hash"),
            "boundary_score": snap.get("boundary_score"),
            "boundary_event": snap.get("boundary_event"),
            "boundary_reason": snap.get("boundary_reason"),
            "Bcrit": snap.get("Bcrit"),
            "replay_K": replay_k,
        },
        "observations": {
            "stability": snap.get("stability"),
            "retention": snap.get("retention"),
            "drift": drift_value,
            "drift_raw": snap.get("drift_raw"),
            "drift_topology": snap.get("drift_topology"),
            "drift_dependency": snap.get("drift_dependency"),
            "delta_stability": delta,
        },
        "replay": replay,
        "outputs": {
            "last_run": "artifacts/last_run.json",
            "replay_k": "artifacts/replay_k.json",
            "history_dir": "artifacts/history/",
            "packet_latest": "docs/feedback/packet_latest.json",
            "docs_ledger": "docs/ledger/docs_ledger.jsonl",
        },
        "invariants_locked": [
            "stability = retention - drift",
            "artifacts/last_run.json overwritten each run",
            "artifacts/replay_k.json overwritten each run",
            "history snapshots append-only",
            "docs_ledger append-only",
        ],
    }

    PACKET_LATEST.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    PACKETS.joinpath(f"packet_{stamp()}.json").write_text(
        json.dumps(packet, indent=2), encoding="utf-8"
    )

    append_jsonl(
        DOCS_LEDGER,
        {
            "t": packet["timestamp"],
            "mode": packet["mode"],
            "stability": packet["observations"]["stability"],
            "retention": packet["observations"]["retention"],
            "drift": packet["observations"]["drift"],
            "boundary_event": packet["episode"]["boundary_event"],
            "boundary_score": packet["episode"]["boundary_score"],
            "packet": "docs/feedback/packet_latest.json",
            "replay_k": "artifacts/replay_k.json",
        },
    )

    return {
        "snapshot_path": str(snap_path),
        "stability": curr_stability,
        "previous_stability": prev_stability,
        "delta": delta,
        "replay_count": replay.get("count"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canonical DDNA loop entrypoint")
    parser.add_argument("--iterations", type=int, default=1, help="number of loop iterations")
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="sleep between iterations",
    )
    parser.add_argument(
        "--forever",
        action="store_true",
        help="run indefinitely until interrupted",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.iterations < 1:
        raise SystemExit("--iterations must be >= 1")

    print("\nDIGITAL-DNA CANONICAL LOOP\n")

    i = 0
    while True:
        i += 1
        result = run_once()
        print(f"Iteration {i}: stability={result['stability']}")
        print(f"Snapshot saved: {result['snapshot_path']}")

        if result["delta"] is None:
            print("Baseline established.")
        else:
            print(
                f"Previous stability: {result['previous_stability']} | "
                f"Delta: {result['delta']}"
            )

        print(f"Replay summary: {REPLAY} (count={result['replay_count']})")
        print(f"Wrote: {PACKET_LATEST}\n")

        if not args.forever and i >= args.iterations:
            break
        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)


if __name__ == "__main__":
    main()
