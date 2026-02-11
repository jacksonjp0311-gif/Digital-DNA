import os
import json

from engine.genome.extract import extract_genome
from engine.drift.topology import extract_topology, compute_topology_drift
from engine.genome.compare import compare_genomes
from engine.genome.normalize import normalize

from engine.stability.compute_S import compute_stability
from engine.stability.retention import retention_ratio

from engine.ledger.append import append_ledger

BASELINE_PATH = 'state/genomes/baseline.json'
LEDGER_PATH = 'ledger/ddna_ledger.jsonl'

def run(target_path):
    current = extract_genome()

    if os.path.exists(BASELINE_PATH):
        with open(BASELINE_PATH) as f:
            baseline = json.load(f)
    else:
        baseline = current
        os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
        with open(BASELINE_PATH, 'w') as f:
            json.dump(current, f)

    common = compare_genomes(current, baseline)
    C = retention_ratio(common, len(baseline))

    # --- Topology Drift Channel ---
    topology = extract_topology()
    topology_drift = compute_topology_drift(topology)

    D = topology_drift

    S = compute_stability(C, D)

    record = {
        'retention': C,
        'drift': D,
        'stability': S
    }

    append_ledger(LEDGER_PATH, record)

    print('DDNA RUN COMPLETE')
    print(record)

if __name__ == '__main__':
    run('.')
