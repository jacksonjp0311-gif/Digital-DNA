import json
from engine.genome.extract import extract_genome
g = extract_genome()
files = g.get("files", [])
assert files and isinstance(files, list), "extract_genome() returned empty or invalid files list"
print(json.dumps({"files": files}, indent=2))
