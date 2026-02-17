import json, math
from pathlib import Path

ARCHIVE_PATH = Path("ecosystem/archive/phenotypes.jsonl")
ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_archive():
    if not ARCHIVE_PATH.exists():
        return []
    rows=[]
    with open(ARCHIVE_PATH,"r",encoding="utf-8") as f:
        for line in f:
            try: rows.append(json.loads(line))
            except: pass
    return rows

def append_archive(row):
    with open(ARCHIVE_PATH,"a",encoding="utf-8") as f:
        f.write(json.dumps(row)+"\n")

def phenotype_from_result(result_path,org,gen):
    with open(result_path,"r",encoding="utf-8") as f:
        r=json.load(f)

    score=float(r.get("score",0))
    size=float(r.get("size",0))
    entropy=float(r.get("entropy",0))
    artifacts=float(r.get("artifact_count",0))

    vec=[score,size,entropy,artifacts]

    return {
        "gen":gen,
        "org":org,
        "score":score,
        "vector":vec,
        "result_path":str(result_path)
    }

def distance(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def novelty_score(vec,archive):
    if not archive: return 0.0
    d=[distance(vec,a["vector"]) for a in archive]
    d.sort(reverse=True)
    k=min(5,len(d))
    return sum(d[:k])/k
