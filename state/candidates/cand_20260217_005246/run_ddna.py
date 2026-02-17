# ===== DDNA_ARCH_KNOBS (PHASE 3) =====
WORK_ITERS = 9669
EVAL_REPEATS = 2
SCORE_MODE = "mode_a"
# =====================================
# === DDNA_PHASE2_ZONES_BEGIN ===
# Multi-zone mutation parameters (sandbox mutates these only)
EVOLVE_DELTA_A = 0.0586
EVOLVE_DELTA_B = -0.0259
WEIGHT_STABILITY = 0.98818
WEIGHT_SPEED       = 0.0
WEIGHT_ERRORS      = 0.0
MODE               = "baseline"   # baseline|fast|deep
# === DDNA_PHASE2_ZONES_END ===
import json,sys,random,statistics
from pathlib import Path

def r(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))

runtime=r(sys.argv[1])
genome=r(sys.argv[2])
episodes=r(sys.argv[3])["episodes"]

def score(fam,p,B,D,R,K):
    a=p.get("a",1);b=p.get("b",1);c=p.get("c",1);d=p.get("d",1)
    if fam=="linear_product":
        return (a*1.01)*(R*B)-b*(D*K)+c*R-d*D
    if fam=="cusp_like":
        return (a*1.01)*(R*B)-b*(D*K)+c*(R*B)**2/(1+d*(D*K)**2)
    return 0

def unpack(x):
    return x["Bcrit"],x["drift_weight"],x["retention_weight"],x["replay_K"]

fam=genome.get("family","linear_product")
params=genome.get("params",{})

scores=[]
for e in episodes:
    B,D,R,K=unpack(e)
    scores.append(score(fam,params,B,D,R,K))


# =========================================================
# GUARANTEED NUMERIC SCORE OUTPUT
# =========================================================

try:
    # try to call score() if it exists
    if callable(score):
        _score_val = score()
    else:
        _score_val = score
except Exception:
    _score_val = 0.0

# mutation zone
EVOLVE_DELTA = 0.27138
_score_val = _score_val + EVOLVE_DELTA



# =========================================================

# === DDNA_PHASE2_EMITTER_BEGIN ===
# =========================================================
# PHASE 2 — GUARANTEED NUMERIC STABILITY OUTPUT
# =========================================================
try:
    # Prefer an already-computed numeric score_value if your engine sets it
    _val = None
    for _name in ["score_value","stability_score","stability","fitness","reward","result","metric"]:
        if _name in globals():
            _val = globals().get(_name)
            break

    # If you only have a callable score(), call it
    if _val is None and "score" in globals() and callable(globals()["score"]):
        _val = globals()["score"]()

    # If score is numeric, use it
    if _val is None and "score" in globals() and not callable(globals()["score"]):
        _val = globals()["score"]

    # Safe defaults for future metrics
    _stability_metric = float(_val) if _val is not None else 0.0
    _speed_metric     = float(globals().get("speed_metric", 0.0) or 0.0)
    _error_metric     = float(globals().get("error_metric", 0.0) or 0.0)

    # Mode hook (future): keep deterministic behavior for now
    _mode = str(globals().get("MODE","baseline"))

    score_value = (
        float(globals().get("WEIGHT_STABILITY", 1.0)) * _stability_metric +
        float(globals().get("WEIGHT_SPEED", 0.0))     * _speed_metric     -
        float(globals().get("WEIGHT_ERRORS", 0.0))    * _error_metric     +
        float(globals().get("EVOLVE_DELTA_A", 0.0))   +
        float(globals().get("EVOLVE_DELTA_B", 0.0))
    )

except Exception:
    score_value = 0.0


# === DDNA_PHASE2_EMITTER_END ===


# === DDNA_STABILITY_BLOCK ===
try:
    _base = 0.0

    if 'score_value' in globals():
        _base = float(score_value)
    elif 'score' in globals() and not callable(score):
        _base = float(score)
    elif 'score' in globals() and callable(score):
        _base = float(score())

except:
    _base = 0.0

EVOLVE_DELTA_A = globals().get('EVOLVE_DELTA_A',0.0)
EVOLVE_DELTA_B = globals().get('EVOLVE_DELTA_B',0.0)
WEIGHT_STABILITY = globals().get('WEIGHT_STABILITY',1.0)

final_score = (_base * WEIGHT_STABILITY) + EVOLVE_DELTA_A + EVOLVE_DELTA_B



# ===== DDNA FINAL SCORE =====
try:
    base = 0.0

    if 'score_value' in globals():
        base = float(score_value)
    elif 'score' in globals() and not callable(score):
        base = float(score)
    elif 'score' in globals() and callable(score):
        base = float(score())
except:
    base = 0.0

A = globals().get('EVOLVE_DELTA_A',0.0)
B = globals().get('EVOLVE_DELTA_B',0.0)
W = globals().get('WEIGHT_STABILITY',1.0)

final_score = (base * W) + A + B


# ============================





# ==================================





# ============================


# ===== DDNA DYNAMIC SCORE CORE =====
import time, random, math


# <<DDNA_MUTABLE_FN_BEGIN>>
def ddna_work(r, mode):
    # SAFE MUTABLE FUNCTION (Phase 5B)
    # Mutations must remain pure math, no IO, no imports, no globals writes.
    if mode == "mode_a":
        return math.sin(r)
    elif mode == "mode_b":
        return math.cos(r) + 0.25*math.sin(r)
    elif mode == "mode_c":
        return math.cos(r)
    else:
        return math.sin(r)
# <<DDNA_MUTABLE_FN_END>>

# <<DDNA_MUTABLE_SCORE_BEGIN>>
def ddna_score(signal, runtime, A, B, W):
    # SAFE MUTABLE SCORER (Phase 5C)
    # No IO, no imports, no globals mutation.
    base = (signal + 1.0) - (runtime * 0.35)
    return (base * float(W)) + float(A) + float(B)
# <<DDNA_MUTABLE_SCORE_END>>
_t0 = time.time()

error_count = 0
success_count = 1

# simulate workload variance
work = 0
for _ in range(5000):
    work += ddna_work(random.random(), SCORE_MODE)

runtime_seconds = time.time() - _t0

try:
    stability_score = float(work % 1)
except:
    stability_score = 0
    error_count += 1

A = globals().get('EVOLVE_DELTA_A',0.0)
B = globals().get('EVOLVE_DELTA_B',0.0)
W = globals().get('WEIGHT_STABILITY',1.0)

base_score = (
    stability_score
    - (runtime_seconds * 0.5)
    - (error_count * 2)
    + (success_count * 1.5)
)

final_score = (base_score * W) + A + B


# ===================================


# ===== DDNA GLOBAL SCORE CORE =====
import time, random, math


# <<DDNA_MUTABLE_FN_BEGIN>>
def ddna_work(r, mode):
    # SAFE MUTABLE FUNCTION (Phase 5B)
    # Mutations must remain pure math, no IO, no imports, no globals writes.
    if mode == "mode_a":
        return math.sin(r)
    elif mode == "mode_b":
        return math.cos(r) + 0.25*math.sin(r)
    elif mode == "mode_c":
        return math.cos(r)
    else:
        return math.sin(r)
# <<DDNA_MUTABLE_FN_END>>

# <<DDNA_MUTABLE_SCORE_BEGIN>>
def ddna_score(signal, runtime, A, B, W):
    # SAFE MUTABLE SCORER (Phase 5C)
    # No IO, no imports, no globals mutation.
    base = (signal + 1.0) - (runtime * 0.35)
    return (base * float(W)) + float(A) + float(B)
# <<DDNA_MUTABLE_SCORE_END>>
_t0 = time.time()

work = 0
for _ in range(5000):
    work += ddna_work(random.random(), SCORE_MODE)

runtime = time.time() - _t0

A = globals().get('EVOLVE_DELTA_A',0.0)
B = globals().get('EVOLVE_DELTA_B',0.0)
W = globals().get('WEIGHT_STABILITY',1.0)

base = (work % 1) - runtime*0.5 + 1.0

score = (base * W) + A + B


# ==================================

# <<DDNA_PHASE4_SEEDED_BEGIN>>
import time, random, math


# <<DDNA_MUTABLE_FN_BEGIN>>
def ddna_work(r, mode):
    # SAFE MUTABLE FUNCTION (Phase 5B)
    # Mutations must remain pure math, no IO, no imports, no globals writes.
    if mode == "mode_a":
        return math.sin(r)
    elif mode == "mode_b":
        return math.cos(r) + 0.25*math.sin(r)
    elif mode == "mode_c":
        return math.cos(r)
    else:
        return math.sin(r)
# <<DDNA_MUTABLE_FN_END>>

# <<DDNA_MUTABLE_SCORE_BEGIN>>
def ddna_score(signal, runtime, A, B, W):
    # SAFE MUTABLE SCORER (Phase 5C)
    # No IO, no imports, no globals mutation.
    base = (signal + 1.0) - (runtime * 0.35)
    return (base * float(W)) + float(A) + float(B)
# <<DDNA_MUTABLE_SCORE_END>>
# ---- knobs ----
WORK_ITERS   = globals().get("WORK_ITERS", 5000)
EVAL_REPEATS = globals().get("EVAL_REPEATS", 3)
SCORE_MODE   = globals().get("SCORE_MODE", "mode_a")

EVOLVE_DELTA_A   = globals().get("EVOLVE_DELTA_A", 0.0)
EVOLVE_DELTA_B   = globals().get("EVOLVE_DELTA_B", 0.0)
WEIGHT_STABILITY = globals().get("WEIGHT_STABILITY", 1.0)

# ---- deterministic seed hook ----
DDNA_SEED = globals().get("DDNA_SEED", None)
if DDNA_SEED is not None:
    try:
        random.seed(int(DDNA_SEED))
    except:
        pass

# clamp
try:
    WORK_ITERS = int(WORK_ITERS)
except:
    WORK_ITERS = 5000
if WORK_ITERS < 250: WORK_ITERS = 250
if WORK_ITERS > 25000: WORK_ITERS = 25000

_t0 = time.time()
work = 0.0

if SCORE_MODE == "mode_a":
    for _ in range(WORK_ITERS):
        work += ddna_work(random.random(), SCORE_MODE)
elif SCORE_MODE == "mode_b":
    for _ in range(WORK_ITERS):
        work += ddna_work(random.random(), SCORE_MODE)
elif SCORE_MODE == "mode_c":
    for _ in range(WORK_ITERS):
        r = random.random()
        work += math.cos(r) * math.cos(r)
else:
    for _ in range(WORK_ITERS):
        work += ddna_work(random.random(), SCORE_MODE)

runtime = time.time() - _t0
signal = (work % 1.0)

base = (signal + 1.0) - (runtime * 0.35)
score = ddna_score(signal, runtime, EVOLVE_DELTA_A, EVOLVE_DELTA_B, WEIGHT_STABILITY)

print("STABILITY:", float(score))
# <<DDNA_PHASE4_SEEDED_END>>















