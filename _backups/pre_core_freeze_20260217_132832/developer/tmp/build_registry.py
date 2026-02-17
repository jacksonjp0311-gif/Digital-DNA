import pathlib, json

root = pathlib.Path("engine")
modules = []

for d in root.iterdir():
    if d.is_dir():
        files = list(d.rglob("*.py"))
        if files:
            modules.append({
                "module": d.name,
                "file_count": len(files)
            })

path = pathlib.Path("developer/module_registry.json")
path.write_text(json.dumps(modules, indent=2))

print("registry written")
