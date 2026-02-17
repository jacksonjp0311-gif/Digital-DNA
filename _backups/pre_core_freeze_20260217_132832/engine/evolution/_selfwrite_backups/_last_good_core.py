import json, random, math, os, time, traceback, hashlib, subprocess, sys
from typing import Dict, Any, List, Tuple

ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVOL   = os.path.abspath(os.path.join(os.path.dirname(__file__)))
MUTDIR = os.path.join(ROOT, "engine", "mutations")
GENOME_PATH = os.path.join(MUTDIR, "genome.json")
META_PATH   = os.path.join(MUTDIR, "meta.json")

BKDIR       = os.path.join(EVOL, "_selfwrite_backups")
LAST_GOOD   = os.path.join(BKDIR, "_last_good_core.py")
TMP_CORE    = os.path.join(EVOL, "_tmp_candidate_core.py")

os.makedirs(BKDIR, exist_ok=True)

# ---------------------------------------
# Stable math primitives (keep deterministic structure; randomness only in r)
# ---------------------------------------
def _rr(x: float) -> float:
    return x / (1.0 + abs(x))

def _sin(x: float) -> float:
    return math.sin(x)

def _cos(x: float) -> float:
    return math.cos(x)

def _sin_rr(x: float) -> float:
    return _sin(_rr(x))

def _cos_rr(x: float) -> float:
    return _cos(_rr(x))

def _cos_sin(x: float) -> float:
    return _cos(x) + 0.35*_sin(x)

def _sin_cos(x: float) -> float:
    return _sin(x) + 0.35*_cos(x)

def _sin_mul_cos(x: float) -> float:
    return _sin(x) * _cos(x)

OPS = {
  "sin": _sin,
  "cos": _cos,
  "sin_rr": _sin_rr,
  "cos_rr": _cos_rr,
  "cos_sin": _cos_sin,
  "sin_cos": _sin_cos,
  "sin_mul_cos": _sin_mul_cos
}

# === AUTO_OPS_BEGIN ===
# (Mode 4 can insert additional ops here safely; always validated by py_compile before swapping.)
# === AUTO_OPS_END ===

# ---------------------------------------
# IO (BOM-safe load)
# ---------------------------------------
def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def _save_json(path: str, obj: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

def load_genome() -> Dict[str, Any]:
    return _load_json(GENOME_PATH)

def save_genome(g: Dict[str, Any]) -> None:
    _save_json(GENOME_PATH, g)

def load_meta() -> Dict[str, Any]:
    return _load_json(META_PATH)

def save_meta(m: Dict[str, Any]) -> None:
    _save_json(META_PATH, m)

# ---------------------------------------
# Scoring
# ---------------------------------------
def score(g: Dict[str, Any], meta: Dict[str, Any]) -> float:
    # r is the only entropy source; keep bounded + smooth
    r = random.random() * math.pi
    A = float(g.get("A", 0.0))
    B = float(g.get("B", 0.0))
    W = float(g.get("W", 1.0))
    ma = str(g.get("mode_a", "sin"))
    mb = str(g.get("mode_b", "cos"))
    mc = str(g.get("mode_c", "sin"))
    fa = OPS.get(ma, _sin)
    fb = OPS.get(mb, _cos)
    fc = OPS.get(mc, _sin)

    mode = str(meta.get("score_mode", "rr_mix"))

    base = fa(r*A) + fb(r*B) + (W * 0.65) + (0.35 * fc(r*(A+B)))
    if mode == "rr_mix":
        return abs(_rr(base) + 0.35*abs(base))
    elif mode == "raw_abs":
        return abs(base)
    else:
        return abs(_rr(base))

# ---------------------------------------
# Mutation (multi-candidate)
# ---------------------------------------
MODE_KEYS = list(OPS.keys())

def mutate(g: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    scale = float(meta.get("mutation_scale", 0.06))
    ng = dict(g)

    ng["A"] = float(ng.get("A", 0.0)) + random.uniform(-scale, scale)
    ng["B"] = float(ng.get("B", 0.0)) + random.uniform(-scale, scale)
    ng["W"] = float(ng.get("W", 1.0)) + random.uniform(-scale, scale)

    # occasional mode flips
    if random.random() < 0.25:
        ng["mode_a"] = random.choice(MODE_KEYS)
    if random.random() < 0.25:
        ng["mode_b"] = random.choice(MODE_KEYS)
    if random.random() < 0.25:
        ng["mode_c"] = random.choice(MODE_KEYS)

    return ng

def confirm(g: Dict[str, Any], meta: Dict[str, Any]) -> float:
    k = int(meta.get("confirm_k", 5))
    s = 0.0
    for _ in range(max(1, k)):
        s += score(g, meta)
    return s / max(1, k)

# ---------------------------------------
# Crash-learning + meta adaptation
# ---------------------------------------
def meta_adapt(meta: Dict[str, Any], promoted: bool, crashed: bool) -> Dict[str, Any]:
    m = dict(meta)
    m["recent_promotes"] = int(m.get("recent_promotes", 0))
    m["recent_crashes"]  = int(m.get("recent_crashes", 0))
    m["crash_penalty"]   = float(m.get("crash_penalty", 0.0))

    if promoted:
        m["recent_promotes"] += 1
        # gently explore more if promoting
        m["mutation_scale"] = min(0.20, float(m.get("mutation_scale", 0.06)) * 1.02)

    if crashed:
        m["recent_crashes"] += 1
        m["crash_penalty"] = min(1000.0, float(m.get("crash_penalty", 0.0)) + 1.0)
        # reduce mutation scale after crashes
        m["mutation_scale"] = max(0.01, float(m.get("mutation_scale", 0.06)) * 0.92)

    # clamp candidates to sane range
    m["k_candidates"] = int(max(3, min(25, int(m.get("k_candidates", 7)))))
    m["confirm_k"]    = int(max(3, min(15, int(m.get("confirm_k", 5)))))
    return m

# ---------------------------------------
# SAFE self-rewrite (only modifies AUTO_OPS region) + py_compile gate
# ---------------------------------------
OP_TEMPLATES = [
    ("op_rr_sin", "def {name}(x: float) -> float:\\n    return math.sin(_rr(x))\\n"),
    ("op_rr_cos", "def {name}(x: float) -> float:\\n    return math.cos(_rr(x))\\n"),
    ("op_mix_a",  "def {name}(x: float) -> float:\\n    return 0.7*math.sin(x) + 0.3*math.cos(_rr(x))\\n"),
    ("op_mix_b",  "def {name}(x: float) -> float:\\n    return 0.7*math.cos(x) + 0.3*math.sin(_rr(x))\\n"),
    ("op_mul",    "def {name}(x: float) -> float:\\n    return math.sin(x) * math.cos(_rr(x))\\n"),
]

def _hash(txt: str) -> str:
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()[:16]

def _compile_ok(path: str) -> bool:
    try:
        # py_compile returns nonzero if syntax fails
        r = subprocess.run([sys.executable, "-m", "py_compile", path], capture_output=True, text=True)
        return (r.returncode == 0)
    except Exception:
        return False

def safe_insert_op_into_core(limit: int) -> Tuple[bool, str]:
    """
    Insert a new operator into AUTO_OPS region, register it in OPS.
    Returns (changed, message).
    """
    path = os.path.abspath(__file__)
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()

    begin = txt.find("# === AUTO_OPS_BEGIN ===")
    end   = txt.find("# === AUTO_OPS_END ===")
    if begin == -1 or end == -1 or end <= begin:
        return (False, "AUTO_OPS markers missing; skipping rewrite")

    region = txt[begin:end]
    # count existing inserted ops (rough heuristic)
    current_inserts = region.count("def op_")
    if current_inserts >= int(limit):
        return (False, f"op_insertion_limit reached ({current_inserts}); skipping rewrite")

    base_name, tpl = random.choice(OP_TEMPLATES)
    name = f"op_{base_name}_{random.randint(1000,9999)}"
    fn_src = tpl.format(name=name)

    # inject into region (just before END marker)
    new_region = region + "\\n" + fn_src + f"OPS['{name}'] = {name}\\n"
    new_txt = txt[:begin] + new_region + txt[end:]

    # write candidate, compile, then commit atomically
    with open(TMP_CORE, "w", encoding="utf-8") as f:
        f.write(new_txt)

    if not _compile_ok(TMP_CORE):
        try:
            os.remove(TMP_CORE)
        except Exception:
            pass
        return (False, "rewrite candidate failed py_compile; rejected")

    # backup last-good (current file) then replace
    try:
        with open(LAST_GOOD, "w", encoding="utf-8") as f:
            f.write(txt)
    except Exception:
        pass

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_txt)

    try:
        os.remove(TMP_CORE)
    except Exception:
        pass

    return (True, f"SAFE_REWRITE accepted: inserted {name}")

# ---------------------------------------
# Public step() API required by loop
# ---------------------------------------
best_confirmed = -1e9

def step(iteration: int) -> Dict[str, Any]:
    global best_confirmed

    crashed = False
    promoted = False
    rewrite_msg = ""

    try:
        g = load_genome()
        meta = load_meta()

        # multi-candidate tournament
        k = int(meta.get("k_candidates", 7))
        candidates: List[Dict[str, Any]] = [mutate(g, meta) for _ in range(max(1, k))]
        # score candidates quickly
        scored: List[Tuple[float, Dict[str, Any]]] = [(score(c, meta), c) for c in candidates]
        scored.sort(key=lambda t: t[0], reverse=True)
        best_cand_score, best_cand = scored[0]

        main_score = score(g, meta)

        # confirm gating
        conf = confirm(best_cand, meta)
        if conf > best_confirmed:
            best_confirmed = conf
            save_genome(best_cand)
            promoted = True

        # periodic self-rewrite (safe; only ops region)
        rp = int(meta.get("rewrite_period", 120))
        if rp > 0 and (iteration % rp == 0):
            changed, msg = safe_insert_op_into_core(int(meta.get("op_insertion_limit", 12)))
            rewrite_msg = msg
            # if changed, also expand available mode keys in genome mutations indirectly (OPS dict grows)

        # periodic meta mutation (no code rewrite)
        mp = int(meta.get("meta_mutation_period", 30))
        if mp > 0 and (iteration % mp == 0):
            # nudge exploration parameters
            m2 = dict(meta)
            if random.random() < 0.50:
                m2["k_candidates"] = int(max(3, min(25, int(m2.get("k_candidates", 7)) + random.choice([-1,1]))))
            if random.random() < 0.50:
                m2["confirm_k"] = int(max(3, min(15, int(m2.get("confirm_k", 5)) + random.choice([-1,1]))))
            if random.random() < 0.40:
                m2["rewrite_period"] = int(max(60, min(600, int(m2.get("rewrite_period", 120)) + random.choice([-30,30,60,-60]))))
            if random.random() < 0.30:
                m2["score_mode"] = random.choice(["rr_mix","raw_abs","rr_only"])
            meta = m2

        meta = meta_adapt(meta, promoted=promoted, crashed=False)
        save_meta(meta)

        return {
            "iter": iteration,
            "main": float(main_score),
            "cand": float(best_cand_score),
            "best_conf": float(best_confirmed),
            "k": int(meta.get("k_candidates", 7)),
            "confirm_k": int(meta.get("confirm_k", 5)),
            "mut_scale": float(meta.get("mutation_scale", 0.06)),
            "rewrite": rewrite_msg
        }

    except Exception as e:
        crashed = True
        try:
            meta = load_meta()
            meta = meta_adapt(meta, promoted=False, crashed=True)
            save_meta(meta)
        except Exception:
            pass
        # bubble the crash (loop/supervisor will log/restart); crash-learning is recorded in meta
        raise