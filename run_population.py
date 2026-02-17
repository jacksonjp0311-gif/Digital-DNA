import json, random, subprocess, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORG_ROOT = ROOT / "organisms"
POP_FILE = ROOT / "population" / "population.json"

def load_population():
    if not POP_FILE.exists():
        return {"generation":0,"size":0}
    try:
        txt = POP_FILE.read_text(encoding="utf-8-sig").strip()
        if not txt:
            return {"generation":0,"size":0}
        return json.loads(txt)
    except:
        return {"generation":0,"size":0}

def run_org(org_dir):
    try:
        out = subprocess.check_output(
            ["python","run.py"],
            cwd=ROOT,
            timeout=20
        ).decode(errors="ignore")

        for line in out.splitlines():
            if "best_raw=" in line:
                return float(line.split("best_raw=")[1].split()[0])
    except:
        return -999999
    return -999999

def main():
    pop = load_population()
    pop["generation"] += 1

    scores = []

    for org in ORG_ROOT.iterdir():
        score = run_org(org)
        scores.append((score, org))

    scores.sort(reverse=True, key=lambda x:x[0])

    best = scores[:2]
    worst = scores[-2:]

    for _, org in worst:
        parent = random.choice(best)[1]
        shutil.rmtree(org)
        shutil.copytree(parent, org)

    POP_FILE.write_text(json.dumps(pop, indent=2))

    print("GEN", pop["generation"], "BEST", best[0][0])

if __name__ == "__main__":
    while True:
        main()
