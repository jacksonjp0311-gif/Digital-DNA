import json
import pathlib

root = pathlib.Path("artifacts/history")
files = sorted(root.glob("run_*.json"))[-5:]

print("\nLAST RUN SNAPSHOT ANALYSIS\n")

for f in files:
    d = json.loads(f.read_text())
    print(f.name)
    print(" stability:", d["stability"])
    print(" drift_total:", d["drift_total"])
    print(" boundary:", d["boundary_event"])
    print()
