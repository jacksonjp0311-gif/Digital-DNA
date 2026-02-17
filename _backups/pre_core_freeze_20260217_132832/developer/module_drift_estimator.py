import json, pathlib

root = pathlib.Path("developer")
registry = json.loads((root / "module_registry.json").read_text())

hist = sorted(pathlib.Path("artifacts/history").glob("run_*.json"))
if len(hist) < 2:
    print("Not enough runs to compare.")
    raise SystemExit

latest = json.loads(hist[-1].read_text())
prev   = json.loads(hist[-2].read_text())

print("\nMODULE STABILITY ESTIMATE\n")

for mod in registry:
    name = mod["module"]
    count = mod["file_count"]

    # heuristic: distribute dependency drift by module size
    drift = latest["drift_total"]
    weight = count / sum(m["file_count"] for m in registry)

    mod_drift = drift * weight

    print(f"{name:20s} files={count:3d}  drift_est={mod_drift:.4f}")
