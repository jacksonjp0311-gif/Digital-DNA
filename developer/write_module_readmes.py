import json, pathlib

registry = json.loads(pathlib.Path("developer/module_registry.json").read_text())
hist = sorted(pathlib.Path("artifacts/history").glob("run_*.json"))
latest = json.loads(hist[-1].read_text())

total_files = sum(m["file_count"] for m in registry)

for mod in registry:
    name  = mod["module"]
    files = mod["file_count"]

    weight = files / total_files
    drift  = latest["drift_total"] * weight
    stability = 1 - drift

    out = f'''
# {name.upper()} MODULE

files: {files}
estimated_stability: {stability:.3f}
role: structural component of Digital-DNA system

This module participates in the invariant-measurement loop.
Stability reflects contribution to global drift surface.
'''

    path = pathlib.Path("developer") / f"README_{name}.md"
    path.write_text(out.strip())
    print("wrote", path)
