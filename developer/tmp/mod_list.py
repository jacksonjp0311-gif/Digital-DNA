import pathlib, json

root = pathlib.Path("engine")
mods = []

for d in root.iterdir():
    if d.is_dir():
        files = list(d.rglob("*.py"))
        if files:
            mods.append({
                "module": d.name,
                "files": [str(f) for f in files]
            })

path = pathlib.Path("developer/module_files.json")
path.write_text(json.dumps(mods, indent=2))
print("module list written")
