import json
from engine.genome.extract import extract_genome
g = extract_genome()
print(json.dumps(g,indent=2))
