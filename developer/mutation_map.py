import json, pathlib

hist = sorted(pathlib.Path("artifacts/history").glob("run_*.json"))
latest = json.loads(hist[-1].read_text())
prev   = json.loads(hist[-2].read_text())

latest_top = set(latest.get("topology_files", []))
prev_top   = set(prev.get("topology_files", []))

added   = latest_top - prev_top
removed = prev_top - latest_top

print("\nMODULE MUTATION MAP\n")

print("Added files:")
for f in sorted(added):
    print(" +", f)

print("\nRemoved files:")
for f in sorted(removed):
    print(" -", f)

print("\nTotal change count:", len(added) + len(removed))
