import json, pathlib, datetime

ROOT = pathlib.Path(".").resolve()

EXCLUDE = {".git", "__pycache__", "node_modules"}

def walk_tree(root):
    files = []
    for p in root.rglob("*"):
        if any(part in EXCLUDE for part in p.parts):
            continue
        if p.is_file():
            files.append(str(p.relative_to(root)))
    return sorted(files)

def module_map(files):
    modules = {}
    for f in files:
        parts = pathlib.Path(f).parts
        if len(parts) < 2:
            continue
        mod = parts[1]
        modules.setdefault(mod, 0)
        modules[mod] += 1
    return modules

files = walk_tree(ROOT)
modules = module_map(files)

# last run snapshot
hist = sorted(pathlib.Path("artifacts/history").glob("run_*.json"))
latest = None
if hist:
    latest = json.loads(hist[-1].read_text())

dump = {
    "timestamp": datetime.datetime.utcnow().isoformat(),
    "file_count": len(files),
    "files": files,
    "modules": modules,
    "latest_run": latest
}

# write json
out_json = pathlib.Path("developer/full_system_dump.json")
out_json.write_text(json.dumps(dump, indent=2))

# write readable text
out_txt = pathlib.Path("developer/full_system_dump.txt")
with out_txt.open("w", encoding="utf8") as f:
    f.write("DIGITAL DNA SYSTEM DUMP\n\n")
    f.write(f"Total files: {len(files)}\n\n")

    f.write("MODULE DISTRIBUTION\n")
    for m,c in modules.items():
        f.write(f"{m:20s} {c}\n")

    f.write("\nLAST RUN SNAPSHOT\n")
    if latest:
        for k,v in latest.items():
            f.write(f"{k}: {v}\n")

    f.write("\nFILE TREE\n")
    for file in files:
        f.write(file + "\n")

print("FULL DUMP WRITTEN → developer/full_system_dump.json")
