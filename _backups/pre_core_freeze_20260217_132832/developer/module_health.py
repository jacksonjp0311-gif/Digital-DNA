import json, pathlib

registry = json.loads(pathlib.Path("developer/module_registry.json").read_text())
hist = sorted(pathlib.Path("artifacts/history").glob("run_*.json"))

latest = json.loads(hist[-1].read_text())

print("\nMODULE HEALTH SNAPSHOT\n")

total_files = sum(m["file_count"] for m in registry)

for mod in registry:
    name  = mod["module"]
    files = mod["file_count"]

    weight = files / total_files
    drift  = latest["drift_total"] * weight
    stability = 1 - drift

    print(f"{name:20s} files={files:3d}  stability_est={stability:.3f}")
