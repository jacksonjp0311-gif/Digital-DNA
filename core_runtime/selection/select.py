from pathlib import Path
from .archive import load_archive,append_archive,phenotype_from_result,novelty_score

RESULT_BASE = Path("ecosystem/runtime")

def collect_phenotypes(gen):
    rows=[]
    for p in RESULT_BASE.glob("org_*/result.json"):
        org=p.parent.name.split("_")[1]
        rows.append(phenotype_from_result(p,org,gen))
    return rows

def select_next_gen(gen):
    archive=load_archive()
    rows=collect_phenotypes(gen)

    for r in rows:
        r["novelty"]=novelty_score(r["vector"],archive)

    for r in rows:
        append_archive(r)

    rows.sort(key=lambda x:x["novelty"],reverse=True)
    novel=rows[:2]

    rows.sort(key=lambda x:x["score"],reverse=True)
    best=rows[:2]

    keep={r["org"]:r for r in novel+best}
    selected=list(keep.values())

    print("")
    print("[SELECT F-MODE]")
    for s in selected:
        print(f"ORG{s['org']} score={s['score']:.3f} novelty={s['novelty']:.3f}")

    return selected
