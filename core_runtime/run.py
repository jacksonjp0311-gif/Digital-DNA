import subprocess
import time
from selection.select import select_next_gen

GEN = 0

def run_generation(gen_id):
    print(f"\n==============================")
    print(f" GENERATION {gen_id}")
    print(f"==============================\n", flush=True)

    # run organisms in parallel
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

    select_next_gen(gen_id)

def main():
    global GEN

    print("\nDIGITAL-DNA EVOLUTION ENGINE ONLINE\n")

    while True:
        run_generation(GEN)
        GEN += 1

if __name__ == "__main__":
    main()
