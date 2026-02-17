import json,random,math,os,time,traceback,shutil

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
GENOME=os.path.join(ROOT,'engine','mutations','genome.json')
CRASHF=os.path.join(ROOT,'engine','evolution','_backups','_crash_state.json')
BACKUP=os.path.join(ROOT,'engine','evolution','_backups','core_last_good.py')

best_conf=-999
trend=[]
iters=0
rewrite_count=0

# ------------------------------------------------------------
def load():
    with open(GENOME,encoding='utf-8-sig') as f:
        return json.load(f)

def save(g):
    with open(GENOME,'w',encoding='utf-8') as f:
        json.dump(g,f,indent=2)

def load_crash():
    if not os.path.exists(CRASHF):
        return {}
    return json.load(open(CRASHF))

def save_crash(s):
    json.dump(s,open(CRASHF,'w'),indent=2)

# ------------------------------------------------------------
def score(g):
    r=random.random()*math.pi
    return abs(math.sin(r*g['A'])+math.cos(r*g['B'])+g['W'])

def mutate(g):
    g=dict(g)
    m=g.get("mutation_scale",0.05)
    g['A']+=random.uniform(-m,m)
    g['B']+=random.uniform(-m,m)
    g['W']+=random.uniform(-m,m)
    return g

# ------------------------------------------------------------
# FIXED adapt_controls — ALWAYS RETURNS 2 VALUES
# ------------------------------------------------------------
def adapt_controls(g, crash_state):
    crash_bias=0.0

    if len(trend)<30:
        return g, crash_bias

    recent=trend[-30:]
    avg=sum(recent)/30

    crashes=int(crash_state.get("crashes",0))
    crash_bias=min(1.0,crashes/10)

    mu=g.get("mutation_scale",0.05)
    k=g.get("k",8)
    ck=g.get("ck",4)

    if avg>2.2:
        mu*=0.99
        k+=1
    else:
        mu*=1.02

    if crash_bias>0:
        mu*=1-(0.1*crash_bias)
        k=max(6,k-1)

    g["mutation_scale"]=max(0.005,min(0.25,mu))
    g["k"]=max(6,min(14,k))
    g["ck"]=max(3,min(7,ck))

    return g, crash_bias

# ------------------------------------------------------------
# PHASE 7 SELF-REWRITE
# ------------------------------------------------------------
def maybe_rewrite():
    global rewrite_count
    if len(trend)<80: return
    avg=sum(trend[-80:])/80
    if avg<2.5: return

    path=__file__
    txt=open(path,'r',encoding='utf-8').read()

    if "mutation_scale" in txt and "0.05" in txt:
        txt=txt.replace("0.05","0.06")
        rewrite_count+=1
        shutil.copy(path,BACKUP)
        open(path,'w',encoding='utf-8').write(txt)
        print("[PHASE7] SELF-REWRITE COMPLETE")

# ------------------------------------------------------------
def crash_learn(err):
    s=load_crash()
    s["crashes"]=int(s.get("crashes",0))+1
    s["last"]=str(err)
    save_crash(s)

# ------------------------------------------------------------
def step(i):
    global best_conf,iters
    iters=i
    try:
        g=load()
        crash=load_crash()

        g,cb=adapt_controls(g,crash)

        main=score(g)
        cand=mutate(g)
        cs=score(cand)

        trend.append(main)

        if cs>best_conf:
            confirm=(score(cand)+score(cand)+score(cand))/3
            if confirm>best_conf:
                best_conf=confirm
                save(cand)
                print(f"PROMOTED iter {i} -> {best_conf:.4f}")

        maybe_rewrite()

        print(f"iter {i} main={main:.4f} cand={cs:.4f} best={best_conf:.4f}")

    except Exception as e:
        print("[CRASH]",e)
        traceback.print_exc()
        crash_learn(e)