import json, pathlib, subprocess, sys

mods = json.loads(pathlib.Path("developer/module_files.json").read_text())

def run_ddna():
    p = subprocess.run(["python","engine/orchestrator/run_ddna.py"], capture_output=True, text=True)
    txt = p.stdout
    s = txt.find("{")
    e = txt.rfind("}")
    if s < 0:
        return None
    return json.loads(txt[s:e+1])

baseline = run_ddna()
base = baseline["drift_total"]

results = []

for m in mods:
    name = m["module"]
    files = m["files"]

    if not files:
        continue

    target = files[0]

    # mutate file
    orig = pathlib.Path(target).read_text()
    pathlib.Path(target).write_text(orig + "\n# drift probe\n")

    out = run_ddna()

    # restore
    pathlib.Path(target).write_text(orig)

    if not out:
        continue

    delta = out["drift_total"] - base

    results.append({
        "module": name,
        "delta": delta
    })

path = pathlib.Path("developer/module_sensitivity.json")
path.write_text(json.dumps(results, indent=2))

print("sensitivity written")
