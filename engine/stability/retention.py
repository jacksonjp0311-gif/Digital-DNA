import json
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[2]

def fingerprint_files(files):
    h = hashlib.sha256()
    for f in sorted(files):
        h.update(f.encode())
    return h.hexdigest()

def compute_retention(genome):
    base_path = ROOT / "state" / "environments" / "topology_baseline.json"
    base = json.loads(base_path.read_text())

    base_files = base.get("files", [])
    base_fp = base.get("fingerprint", "")

    cur_files = genome.get("files", [])
    cur_fp = fingerprint_files(cur_files)

    if not base_files:
        return 1.0

    overlap = len(set(base_files) & set(cur_files))
    total = len(set(base_files) | set(cur_files))

    similarity = overlap / total if total else 1.0

    return similarity
