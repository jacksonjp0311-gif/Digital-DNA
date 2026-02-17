import json, pathlib

registry = json.loads(open("developer/module_registry.json").read())
hist = sorted(pathlib.Path("artifacts/history").glob("run_*.json"))

if not hist:
    print("No runs found")
    raise SystemExit

latest = json.loads(hist[-1].read_text())

total_files = sum(m["file_count"] for m in registry)

print("\nWEIGHTED MODULE DRIFT\n")

for mod in registry:
    name = mod["module"]
    files = mod["file_count"]

    weight = files / total_files
    drift = latest["drift_total"] * weight
    stability = 1 - drift

    print(f"{name:20s} weight={weight:.3f} stability={stability:.3f}")
