import os, json, random, math, time, traceback, shutil, sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVOL_DIR = os.path.join(ROOT, "engine", "evolution")
BK_DIR   = os.path.join(EVOL_DIR, "_selfwrite_backups")
GENOME   = os.path.join(ROOT, "engine", "mutations", "genome.json")

os.makedirs(BK_DIR, exist_ok=True)

best_raw = -1e18
best_conf = -1e18
promotes = 0

def _read_json_bomsafe(path):
    # Accept UTF-8 and UTF-8-BOM
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def load_genome():
    g = _read_json_bomsafe(GENOME)
    # defaults (in case file gets mutated externally)
    g.setdefault("A", 0.5); g.setdefault("B", 0.5); g.setdefault("W", 1.0)
    g.setdefault("mode_a", "sin"); g.setdefault("mode_b", "cos"); g.setdefault("mode_c", "sin")
    g.setdefault("rewrite_every", 25)
    g.setdefault("mutation_strength", 1.0)
    g.setdefault("confirm_k", 3)
    return g

def save_genome(g):
    # Write NO-BOM utf-8
    with open(GENOME, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, indent=2, sort_keys=True)

def _f(mode, x):
    # small function library
    if mode == "sin": return math.sin(x)
    if mode == "cos": return math.cos(x)
    if mode == "sin_cos": return math.sin(x) + math.cos(0.5*x)
    if mode == "cos_sin": return math.cos(x) + math.sin(0.5*x)
    if mode == "sin_rr": return math.sin(x) * (1.0 + 0.1*random.random())
    if mode == "cos_rr": return math.cos(x) * (1.0 + 0.1*random.random())
    if mode == "sin_mul_cos": return math.sin(x) * math.cos(x)
    # default
    return math.sin(x)

def score(g):
    # -------- MUTATE_REGION_BEGIN --------
    # The self-writer mutates ONLY inside this region (still chaotic, but survivable)
    # It can change constants, operators, mode mixing, etc.
    r = random.random() * math.pi
    x = r * g["A"]
    y = r * g["B"]
    z = r * g["W"]

    a = _f(g.get("mode_a","sin"), x)
    b = _f(g.get("mode_b","cos"), y)
    c = _f(g.get("mode_c","sin"), z)

    # A chaotic but bounded objective:
    s = abs(a + b + c) + 0.01*abs(a*b) + 0.01*abs(b*c) + 0.01*abs(c*a)
    # -------- MUTATE_REGION_END --------
    return float(s)

def mutate_genome(g):
    g = dict(g)
    strength = float(g.get("mutation_strength", 1.0))
    # genome drift
    g["A"] = float(g.get("A",0.0)) + random.uniform(-0.10, 0.10) * strength
    g["B"] = float(g.get("B",0.0)) + random.uniform(-0.10, 0.10) * strength
    g["W"] = float(g.get("W",0.0)) + random.uniform(-0.10, 0.10) * strength

    # random function mode mutation
    modes = ["sin","cos","sin_cos","cos_sin","sin_rr","cos_rr","sin_mul_cos"]
    if random.random() < 0.7: g["mode_a"] = random.choice(modes)
    if random.random() < 0.7: g["mode_b"] = random.choice(modes)
    if random.random() < 0.7: g["mode_c"] = random.choice(modes)

    # chaos knobs can evolve too
    if random.random() < 0.3: g["rewrite_every"] = max(5, int(g.get("rewrite_every",25) + random.choice([-5,-3,-1,1,3,5])))
    if random.random() < 0.3: g["confirm_k"] = max(1, int(g.get("confirm_k",3) + random.choice([-2,-1,1,2])))
    if random.random() < 0.3: g["mutation_strength"] = max(0.05, float(g.get("mutation_strength",1.0)) + random.uniform(-0.25, 0.25))
    return g

def _backup_self(tag=""):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    base = os.path.join(BK_DIR, f"evolution_core_{ts}{('_'+tag) if tag else ''}.py")
    shutil.copy2(__file__, base)
    # keep a pointer to "last good"
    shutil.copy2(__file__, os.path.join(BK_DIR, "_last_good.py"))
    return base

def _restore_last_good():
    lg = os.path.join(BK_DIR, "_last_good.py")
    if os.path.exists(lg):
        shutil.copy2(lg, __file__)
        return True
    return False

def _mutate_region_text(txt, strength=1.0):
    """
    Brutal text-level mutation inside MUTATE_REGION.
    - random operator swaps
    - random constant perturbations
    - random line shuffles (small)
    - random token injections
    """
    begin = txt.find("# -------- MUTATE_REGION_BEGIN --------")
    end   = txt.find("# -------- MUTATE_REGION_END --------")
    if begin == -1 or end == -1 or end <= begin:
        return txt

    head = txt[:begin]
    mid  = txt[begin:end]
    tail = txt[end:]

    lines = mid.splitlines()

    # small pool of aggressive edits
    def op_swap(s):
        swaps = [
            (" + ", " - "), (" - ", " + "),
            (" * ", " + "), (" + ", " * "),
            ("0.01", str(max(0.0001, 0.01 + random.uniform(-0.008, 0.05)*strength))),
            ("math.pi", "math.tau" if hasattr(math,"tau") else "math.pi*2"),
            ("abs(", "math.fabs("),
            ("0.5*x", f"{max(0.05, 0.5 + random.uniform(-0.4,0.9)*strength):.3f}*x"),
        ]
        a,b = random.choice(swaps)
        return s.replace(a,b,1) if a in s else s

    # apply several random edits
    edits = max(1, int(2 + 6*random.random()*strength))
    for _ in range(edits):
        i = random.randrange(len(lines))
        lines[i] = op_swap(lines[i])

    # occasional line shuffle inside region (limited)
    if random.random() < 0.25*strength and len(lines) > 6:
        a = random.randrange(1, len(lines)-1)
        b = random.randrange(1, len(lines)-1)
        lines[a], lines[b] = lines[b], lines[a]

    # occasional injection of a new line (dangerous but fun)
    if random.random() < 0.20*strength:
        injects = [
            "    s = s + 0.001*abs(a-b) + 0.001*abs(b-c) + 0.001*abs(c-a)",
            "    s = s * (1.0 + 0.01*random.random())",
            "    s = max(s, 0.000001)",
            "    s = s + 0.0001*(a*a + b*b + c*c)",
        ]
        lines.insert(random.randrange(1, len(lines)-1), random.choice(injects))

    new_mid = "\n".join(lines) + "\n"
    return head + new_mid + tail

def rewrite_self(genome):
    """
    Mutate evolution_core.py IN PLACE.
    If it breaks, the supervisor (loop) will restore last-good.
    """
    strength = float(genome.get("mutation_strength", 1.0))
    with open(__file__, "r", encoding="utf-8") as f:
        txt = f.read()

    _backup_self("pre_mut")
    mutated = _mutate_region_text(txt, strength=strength)

    with open(__file__, "w", encoding="utf-8", newline="\n") as f:
        f.write(mutated)

def step(i):
    global best_raw, best_conf, promotes

    g = load_genome()
    cand = mutate_genome(g)

    main_score = score(g)
    cand_score = score(cand)

    if cand_score > best_raw:
        best_raw = cand_score

    # confirmation gate (still chaotic, but stops constant thrash)
    if cand_score > best_conf:
        k = int(cand.get("confirm_k", 3))
        k = max(1, min(15, k))
        conf = sum(score(cand) for _ in range(k)) / float(k)
        if conf > best_conf:
            best_conf = conf
            promotes += 1
            save_genome(cand)
            print(f"PROMOTED iter {i} CONFIRMED -> {best_conf:.6f}  promotes={promotes}")

    # periodic self-rewrite (CHAOS MODE)
    rw = int(g.get("rewrite_every", 25))
    rw = max(3, min(500, rw))
    if i % rw == 0:
        print(f"SELF-WRITE TRIGGER iter {i} (rewrite_every={rw})")
        rewrite_self(g)

    print(f"iter {i} main={main_score:.6f} cand={cand_score:.6f} | best_raw={best_raw:.6f} best_conf={best_conf:.6f}")