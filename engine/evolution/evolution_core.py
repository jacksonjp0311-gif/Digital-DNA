import json, os, time, random, math, traceback

ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GENOME = os.path.join(ROOT, "engine", "mutations", "genome.json")
CRASH  = os.path.join(ROOT, "engine", "evolution", "crash_state.json")
BKDIR  = os.path.join(ROOT, "engine", "evolution", "_selfwrite_backups")
LASTGOOD = os.path.join(BKDIR, "_last_good.py")

# rewrite contracts
REWRITE_MIN_ITERS = 120
REWRITE_MIN_PLATEAU = 35
REWRITE_MAX_DELTA = 0.0100  # only tiny constant nudges

def _read_json(path, default):
  try:
    with open(path, "r", encoding="utf-8-sig") as f:
      return json.load(f)
  except Exception:
    return default

def _write_json(path, obj):
  with open(path, "w", encoding="utf-8") as f:
    json.dump(obj, f, indent=2)

def load_genome():
  g = _read_json(GENOME, {})
  g.setdefault("A", 0.50)
  g.setdefault("B", 0.50)
  g.setdefault("W", 1.00)
  g.setdefault("k", 8)
  g.setdefault("ck", 5)
  g.setdefault("mutation_scale", 0.0400)
  g.setdefault("best_confirmed", -9999.0)
  g.setdefault("best_raw", -9999.0)
  g.setdefault("rewrite_count", 0)
  g.setdefault("phase", 7)
  g.setdefault("trend_hist", [])
  return g

def save_genome(g):
  # cap trend_hist size
  th = g.get("trend_hist", [])
  if isinstance(th, list) and len(th) > 500:
    g["trend_hist"] = th[-500:]
  _write_json(GENOME, g)

def load_crash():
  return _read_json(CRASH, {"crashes":0,"last_error":"","last_iter":0,"last_time":0})

def save_crash(s):
  _write_json(CRASH, s)

def crash_learn(err_text: str, iters: int):
  s = load_crash()
  s["crashes"]   = int(s.get("crashes", 0)) + 1
  s["last_error"]= (err_text or "")[:1200]
  s["last_iter"] = int(iters or 0)
  s["last_time"] = int(time.time())
  save_crash(s)

def backup_last_good():
  os.makedirs(BKDIR, exist_ok=True)
  try:
    with open(__file__, "r", encoding="utf-8") as f:
      txt = f.read()
    with open(LASTGOOD, "w", encoding="utf-8") as f:
      f.write(txt)
  except Exception:
    pass

def restore_last_good():
  try:
    with open(LASTGOOD, "r", encoding="utf-8") as f:
      txt = f.read()
    with open(__file__, "w", encoding="utf-8") as f:
      f.write(txt)
    return True
  except Exception:
    return False

def restore_last_good_if_needed():
  try:
    with open(__file__, "r", encoding="utf-8") as f:
      txt = f.read()
    if "def step" not in txt:
      restore_last_good()
      return True
  except Exception:
    restore_last_good()
    return True
  return False

def score(g):
  r = random.random() * math.pi
  return abs(math.sin(r*g["A"]) + math.cos(r*g["B"]) + g["W"])

def mutate(g):
  mu = float(g.get("mutation_scale", 0.04))
  gg = dict(g)
  gg["A"] = float(gg["A"]) + random.uniform(-mu, mu)
  gg["B"] = float(gg["B"]) + random.uniform(-mu, mu)
  gg["W"] = float(gg["W"]) + random.uniform(-mu, mu)
  return gg

def confirm(g, ck):
  s = 0.0
  for _ in range(int(ck)):
    s += score(g)
  return s / float(ck)

def adapt_controls(g, crash_state):
  gg = dict(g)
  c = int(crash_state.get("crashes", 0))
  crash_bias = min(0.25, 0.01 * float(c))

  mu = float(gg.get("mutation_scale", 0.04))
  mu = max(0.005, mu * (1.0 - crash_bias))
  gg["mutation_scale"] = mu

  gg["k"]  = int(max(3, min(12, int(gg.get("k", 8)))))
  gg["ck"] = int(max(3, min(9,  int(gg.get("ck", 5)))))
  return gg, crash_bias

def plateau_ok(trend_hist):
  if not isinstance(trend_hist, list):
    return False
  if len(trend_hist) < REWRITE_MIN_PLATEAU:
    return False
  w = trend_hist[-REWRITE_MIN_PLATEAU:]
  mx = max(w)
  mn = min(w)
  return (mx - mn) < 0.0200

def safe_rewrite_constants(g):
  # Mode C: tiny nudges only; always backup+restore path; never remove step()
  try:
    # gating
    iters = int(g.get("_iters", 0))
    if iters < REWRITE_MIN_ITERS:
      return False

    th = g.get("trend_hist", [])
    if not plateau_ok(th):
      return False

    backup_last_good()

    # read this file
    with open(__file__, "r", encoding="utf-8") as f:
      txt = f.read()

    # choose a tiny nudge to mutation_scale floor by adjusting REWRITE_MAX_DELTA
    # (kept extremely safe and bounded)
    new_val = REWRITE_MAX_DELTA + random.uniform(-0.0010, 0.0010)
    new_val = max(0.0060, min(0.0200, new_val))

    # rewrite the constant line
    import re
    pat = r"REWRITE_MAX_DELTA\s*=\s*([0-9.]+)"
    m = re.search(pat, txt)
    if not m:
      return False

    old = float(m.group(1))
    if abs(new_val - old) > REWRITE_MAX_DELTA:
      return False

    txt2 = re.sub(pat, f"REWRITE_MAX_DELTA = {new_val:.4f}", txt, count=1)

    # sanity: must still contain def step
    if "def step" not in txt2:
      return False

    # write and quick self-import check via text scan (runtime import happens next loop)
    with open(__file__, "w", encoding="utf-8") as f:
      f.write(txt2)

    g["rewrite_count"] = int(g.get("rewrite_count", 0)) + 1
    return True
  except Exception:
    # restore on any failure
    restore_last_good()
    return False

def selftest():
  g = load_genome()
  s = load_crash()
  out = adapt_controls(g, s)
  ok = (isinstance(out, tuple) and len(out) == 2)
  if not ok:
    return False, "adapt_controls must return (g, crash_bias)"
  return True, "ok"

def step(i):
  g = load_genome()
  crash_state = load_crash()
  g, crash_bias = adapt_controls(g, crash_state)

  k  = int(g.get("k", 8))
  ck = int(g.get("ck", 5))

  best_conf = float(g.get("best_confirmed", -9999.0))
  best_raw  = float(g.get("best_raw", -9999.0))

  main_score = score(g)

  # multi-candidate selection
  cand_best = None
  cand_best_raw = -9999.0
  for _ in range(k):
    cnd = mutate(g)
    sraw = score(cnd)
    if sraw > cand_best_raw:
      cand_best_raw = sraw
      cand_best = cnd

  cand_score = cand_best_raw
  if cand_score > best_raw:
    best_raw = cand_score

  # confirm-gate promotion
  if cand_score > best_conf:
    cconf = confirm(cand_best, ck)
    if cconf > best_conf:
      best_conf = cconf
      g = dict(cand_best)

  # trend / plateau tracking
  th = g.get("trend_hist", [])
  if not isinstance(th, list):
    th = []
  th.append(float(main_score))
  g["trend_hist"] = th
  g["_iters"] = int(i)

  g["best_confirmed"] = best_conf
  g["best_raw"] = best_raw
  g["phase"] = 7

  did = safe_rewrite_constants(g)
  if did:
    print(f"[PHASE7] SELF-REWRITE COMPLETE rewrites={g.get('rewrite_count',0)}")

  save_genome(g)

  print(f"iter {i} main={main_score:.4f} cand={cand_score:.4f} best_conf={best_conf:.4f} best_raw={best_raw:.4f} k={k} ck={ck} mu={g['mutation_scale']:.4f} crash_bias={crash_bias:.4f}")


# ------------------------------------------------------------
# CANONICAL CORE WRAPPER (AUTO-INJECTED)
# Contract: evolution_loop expects build_core() OR class with .step()
# ------------------------------------------------------------

def build_core():
    # Try common class names
    for name in ("EvolutionCore", "Core", "Engine"):
        obj = globals().get(name, None)
        if obj is not None:
            try:
                inst = obj()
                if hasattr(inst, "step"):
                    return inst
            except Exception:
                pass

    # Try module-level step(i)
    fn = globals().get("step", None)
    if callable(fn):
        class _CoreWrapper:
            def step(self, i):
                return fn(i)
        return _CoreWrapper()

    raise RuntimeError("No usable core object found in evolution_core.py")
# [DDNA_MUTATION_MARK]      
