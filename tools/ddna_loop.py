from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import sys

from engine.episodic.replay import write_replay_summary
from engine.episodic.context import read_thresholds

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine" / "orchestrator" / "run_ddna.py"

ART = ROOT / "artifacts"
HIST = ART / "history"
LAST = ART / "last_run.json"
REPLAY = ART / "replay_k.json"

DOCS = ROOT / "docs"
FEEDBACK = DOCS / "feedback"
PACKETS = FEEDBACK / "packets"
DOCS_LEDGER = DOCS / "ledger" / "docs_ledger.jsonl"
PACKET_LATEST = FEEDBACK / "packet_latest.json"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dirs():
    for p in [ART, HIST, FEEDBACK, PACKETS, DOCS / "ledger"]:
        p.mkdir(parents=True, exist_ok=True)

def run_engine():
    if not ENGINE.exists():
        raise FileNotFoundError(str(ENGINE))
    subprocess.run([sys.executable, str(ENGINE)], cwd=str(ROOT), check=True)

def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def append_jsonl(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\\n")

def main():
    ensure_dirs()
    thresholds = read_thresholds()
    K = int(thresholds.get("replay_K", 10))

    print("\\nDIGITAL-DNA PY LOOP\\n")
    run_engine()

    if not LAST.exists():
        raise RuntimeError("Engine did not produce artifacts/last_run.json")

    snap = read_json(LAST) or {}
    snap_path = HIST / f"run_{stamp()}.json"
    snap_path.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    print(f"\\nSnapshot saved: {snap_path}")

    # replay summary (explicit operator)
    replay = write_replay_summary(K)
    print(f"Replay summary: {REPLAY} (count={replay.get('count')})")

    # trend (last delta)
    files = sorted(HIST.glob("run_*.json"))
    if len(files) >= 2:
        a = read_json(files[-2]) or {}
        b = read_json(files[-1]) or {}
        da = float(a.get("stability", 0.0))
        db = float(b.get("stability", 0.0))
        print(f"\\nPrevious stability: {da}")
        print(f"Current  stability: {db}")
        print(f"Delta: {db - da}")
    else:
        print("\\nBaseline established.")

    # packet_latest for Codex ingestion
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
            "replay_K": snap.get("replay_K"),
        },
        "observations": {
            "stability": snap.get("stability"),
            "retention": snap.get("retention"),
            "drift_total": snap.get("drift_total"),
            "drift_topology": snap.get("drift_topology"),
            "drift_dependency": snap.get("drift_dependency"),
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
            "stability = retention - drift_total",
            "artifacts/last_run.json overwritten each run",
            "artifacts/replay_k.json overwritten each run",
            "history snapshots append-only",
            "docs_ledger append-only"
        ]
    }

    PACKET_LATEST.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    PACKETS.joinpath(f"packet_{stamp()}.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")

    append_jsonl(DOCS_LEDGER, {
        "t": packet["timestamp"],
        "mode": packet["mode"],
        "stability": packet["observations"]["stability"],
        "retention": packet["observations"]["retention"],
        "drift_total": packet["observations"]["drift_total"],
        "boundary_event": packet["episode"]["boundary_event"],
        "boundary_score": packet["episode"]["boundary_score"],
        "packet": "docs/feedback/packet_latest.json",
        "replay_k": "artifacts/replay_k.json"
    })

    print(f"\\nWrote: {PACKET_LATEST}")
    print("Done.\\n")

if __name__ == "__main__":
    main()