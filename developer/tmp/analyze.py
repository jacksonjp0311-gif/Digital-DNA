import json, pathlib

hist = sorted(pathlib.Path("artifacts/history").glob("run_*.json"))[-5:]

print("\nLAST RUN ANALYSIS\n")

for f in hist:
    d = json.loads(f.read_text())
    print(f.name)
    print(" stability:", d["stability"])
    print(" drift_total:", d["drift_total"])
    print(" boundary:", d["boundary_event"])
    print()
