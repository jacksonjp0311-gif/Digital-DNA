import os, json, subprocess, time, sys

ROOT = r"C:\Users\jacks\OneDrive\Desktop\Digital-DNA"
LOOP = r"C:\Users\jacks\OneDrive\Desktop\Digital-DNA\engine\evolution\evolution_loop.py"
GENOME = r"C:\Users\jacks\OneDrive\Desktop\Digital-DNA\engine\mutations\genome.json"

def ensure_genome():
    if not os.path.exists(GENOME) or os.path.getsize(GENOME)==0:
        g={"A":0.5,"B":0.5,"W":1.0,"mode_a":"sin","mode_b":"cos","mode_c":"sin"}
        with open(GENOME,"w") as f: json.dump(g,f,indent=2)

print("DDNA SAFE BOOT ACTIVE")

while True:
    try:
        ensure_genome()
        subprocess.run([sys.executable, LOOP], check=True)
    except Exception as e:
        print("LOOP CRASH:", e)
        time.sleep(2)
