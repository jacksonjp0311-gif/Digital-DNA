import json, pathlib

hist = sorted(pathlib.Path("artifacts/history").glob("run_*.json"))
latest = json.loads(hist[-1].read_text())
prev   = json.loads(hist[-2].read_text())

print("\nSTRUCTURAL DIFF\n")

print("Stability delta:", latest["stability"] - prev["stability"])
print("Drift delta:", latest["drift_total"] - prev["drift_total"])
print("Boundary:", latest["boundary_event"])
