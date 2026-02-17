import json, pathlib

sens = json.loads(pathlib.Path("developer/module_sensitivity.json").read_text())

print("\nDRIFT SENSITIVITY REPORT\n")

for s in sens:
    print(f"{s['module']:16s} delta={s['delta']:.6f}")
