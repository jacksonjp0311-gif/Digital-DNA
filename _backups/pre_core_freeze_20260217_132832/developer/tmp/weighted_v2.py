import json, pathlib
registry_path = pathlib.Path("developer/module_registry.json")
if not registry_path.exists():
    print("module_registry.json missing (run registry step first)")
    raise SystemExit
registry = json.loads(registry_path.read_text())
hist = sorted(pathlib.Path("artifacts/history").glob("run_*.json"))
latest = json.loads(hist[-1].read_text())
total_files = sum(m["file_count"] for m in registry)
print("WEIGHTED MODULE DRIFT")
for mod in registry:
    name = mod["module"]
    files = mod["file_count"]
    w = files / total_files
    drift = latest["drift_total"] * w
    stability = 1 - drift
    print(f"{name:16s} w={w:.3f} stability={stability:.3f}")
