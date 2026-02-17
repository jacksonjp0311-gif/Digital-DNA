import json

registry = json.load(open("developer/module_registry.json"))

print("\nDDNA STRUCTURAL MAP\n")

for m in registry:
    print(f"{m['module']:15s} -> {m['file_count']} files")
