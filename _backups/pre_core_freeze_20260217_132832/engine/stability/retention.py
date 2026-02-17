import hashlib
from pathlib import Path

EXCLUDE = {
    "config",
    "DDNA_EVO_SANDBOX",
    "artifacts",
    "__pycache__",
    ".git",
    ".venv",
    "venv"
}

def file_hash(p):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def allowed(p, root):
    try:
        rel = p.relative_to(root)
        return not any(part in EXCLUDE for part in rel.parts)
    except Exception:
        return False

def compute_retention(orig_dir, new_dir):
    orig = Path(orig_dir)
    new  = Path(new_dir)

    orig_files = sorted([p for p in orig.rglob("*") if p.is_file() and allowed(p, orig)])
    new_files  = sorted([p for p in new.rglob("*")  if p.is_file() and allowed(p, new)])

    if not orig_files or not new_files:
        return 0.0

    matches = 0
    total   = 0

    for of in orig_files:
        rel = of.relative_to(orig)
        nf = new / rel

        if nf.exists():
            total += 1
            if file_hash(of) == file_hash(nf):
                matches += 1

    if total == 0:
        return 0.0

    return matches / total
