from pathlib import Path

def extract_genome(root=None):
    """
    Genome extraction (v2.1):
    - produces a stable file-list fingerprint basis for retention.
    - excludes .git and __pycache__.
    """
    if root is None:
        root = Path.cwd()
    else:
        root = Path(root)

    files = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        s = str(p).replace("\\", "/")
        if "/.git/" in s or s.endswith("/.git"):
            continue
        if "/__pycache__/" in s:
            continue
        # keep only code + config-ish artifacts for now
        if p.suffix.lower() in {".py", ".ps1", ".json", ".jsonl", ".md", ".tex", ".txt"}:
            files.append(str(p.relative_to(root)).replace("\\", "/"))

    genome = {
        "files": sorted(files),
        "modules": [],
        "timestamp": str(root)
    }
    return genome
