import subprocess, time, json, os
from pathlib import Path
from selection.select import select_next_gen

POP_SIZE = 4
STEPS = 200

def run_generation(gen_id):
    print(f"\n=== GENERATION {gen_id} ===\n", flush=True)

    p = subprocess.Popen(
        ["python","run_parallel.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in p.stdout:
        print(line.rstrip(), flush=True)

    p.wait()

    print("\n[GENERATION COMPLETE — selecting]\n", flush=True)
    selected = select_next_gen(gen_id)
    return selected

def main():
    gen = 0
    while True:
        run_generation(gen)
        gen += 1

if __name__ == "__main__":
    main()
