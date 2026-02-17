import json, subprocess, random, time, re

GENOME = r"C:\Users\jacks\OneDrive\Desktop\Digital-DNA\engine\genome.json"
ENGINE = r"C:\Users\jacks\OneDrive\Desktop\Digital-DNA\engine\orchestrator\run_ddna.py"

modes = ["sin","cos","sin2","mix"]

try:
    best = json.load(open(GENOME))
    best_score = -999
except:
    best = {"A":0.5,"B":0.5,"W":1.0,"mode_a":"sin","mode_b":"cos","mode_c":"sin"}
    best_score = -999

iteration = 0
print("SANDBOX EVOLUTION ACTIVE")

while True:
    iteration+=1

    cand = dict(best)

    # param mutate
    cand["A"] += random.uniform(-0.05,0.05)
    cand["B"] += random.uniform(-0.05,0.05)
    cand["W"] += random.uniform(-0.05,0.05)

    # func mutate
    cand["mode_a"] = random.choice(modes)
    cand["mode_b"] = random.choice(modes)
    cand["mode_c"] = random.choice(modes)

    json.dump(cand, open(GENOME,"w"))

    try:
        out = subprocess.check_output(["python",ENGINE], text=True)
        m = re.search(r"STABILITY:\s*([0-9\.]+)",out)
        score = float(m.group(1)) if m else -999
    except:
        score = -999

    if score > best_score:
        best_score = score
        best = cand
        json.dump(best, open(GENOME,"w"))
        print(f"PROMOTED iter {iteration} | best={best_score:.6f}")

    print(f"iter {iteration} main={score:.6f} best={best_score:.6f}")

    time.sleep(0.5)
