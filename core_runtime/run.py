import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / "engine"

sys.path.append(str(ENGINE))
sys.path.append(str(ENGINE / "ecosystem"))
sys.path.append(str(ENGINE / "evolution"))

from ecosystem import supervisor

if __name__ == "__main__":
    supervisor.main()

# ================= PERSISTENT_LOOP =================
best_prev=None

for gen in range(GENERATIONS):
    print(f"[GEN] {gen+1}/{GENERATIONS}")

    _parallel_run(org_paths,STEPS)

    results=[]
    for i,p in enumerate(org_paths):
        try:
            data=json.loads((Path(p)/"result.json").read_text())
            results.append((i,data.get("score",0)))
        except:
            results.append((i,0))

    results.sort(key=lambda x:x[1],reverse=True)
    best_id,best_score = results[0]

    best_genome=json.loads((Path(org_paths[best_id])/"genome.json").read_text())

    _record_lineage(best_score,best_genome)

    mut=_adaptive_mutation(best_prev,best_score)
    best_prev=best_score

    for i,_ in results[1:]:
        g=best_genome.copy()
        g["mutation_bias"] += random.uniform(-mut,mut)
        g["param_step_delay"]=max(0.002,g["param_step_delay"]+random.uniform(-mut,mut))
        Path(org_paths[i]).joinpath("genome.json").write_text(json.dumps(g,indent=2))

# =====================================================
