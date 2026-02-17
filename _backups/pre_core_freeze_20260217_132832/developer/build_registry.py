import json, pathlib

root = pathlib.Path("engine")

modules = {}

for p in root.rglob("*.py"):
    parts = p.parts
    if len(parts) < 2:
        continue

    module = parts[1] if parts[0] == "engine" else parts[0]
    modules.setdefault(module, []).append(str(p).replace("\\","/"))

out = []
for m, files in modules.items():
    out.append({
        "module": m,
        "file_count": len(files),
        "files": sorted(files)
    })

pathlib.Path("developer/module_registry.json").write_text(
    json.dumps(out, indent=2)
)

print("Module registry written -> developer/module_registry.json")
