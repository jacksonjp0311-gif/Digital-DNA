import os, sys, json, time, subprocess, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # .../engine/ecosystem -> repo root
LOOP = ROOT / "engine" / "evolution" / "evolution_loop.py"

LOGDIR = ROOT / "logs"
LOGDIR.mkdir(exist_ok=True)
BOOTLOG = LOGDIR / "ecosystem_boot.log"

ECOSTATE = ROOT / "ecosystem" / "state"
RUNS = ECOSTATE / "runs"
RUNS.mkdir(parents=True, exist_ok=True)

POP_FILE = ECOSTATE / "population.json"

def _append(text: str) -> None:
    with open(BOOTLOG, "a", encoding="utf-8") as f:
        f.write(text)

def _p(msg: str) -> None:
    print(msg)
    _append(msg + "\n")

def _fatal(msg: str, code: int = 1) -> None:
    _p("[FATAL] " + msg)
    raise SystemExit(code)

def _default_population(pop_size=4, generations=50, steps=200, watchdog=60):
    return {
        "config": {
            "pop_size": int(pop_size),
            "generations": int(generations),
            "steps": int(steps),
            "watchdog_seconds": int(watchdog),
            "genome_template": {"alpha": 0.50, "beta": 0.50, "mut_rate": 0.05},
        },
        "state": {
            "generation": 0,
            "best_id": None,
            "best_score": None,
            "best_genome": None,
            "history": []
        }
    }

def _load_or_migrate_population(pop_size, generations, steps, watchdog):
    if not POP_FILE.exists():
        pop = _default_population(pop_size, generations, steps, watchdog)
        POP_FILE.parent.mkdir(parents=True, exist_ok=True)
        POP_FILE.write_text(json.dumps(pop, indent=2), encoding="utf-8")
        return pop

    try:
        pop = json.loads(POP_FILE.read_text(encoding="utf-8"))
    except Exception:
        # if corrupted, keep a bad copy and recreate
        bad = POP_FILE.with_suffix(".bad.json")
        bad.write_text(POP_FILE.read_text(errors="ignore"), encoding="utf-8")
        pop = _default_population(pop_size, generations, steps, watchdog)

    if "config" not in pop:
        # MIGRATION: old schema ? new schema
        migrated = _default_population(pop_size, generations, steps, watchdog)
        migrated["state"]["history"] = pop.get("history", pop.get("state", {}).get("history", []))
        migrated["state"]["generation"] = pop.get("generation", pop.get("state", {}).get("generation", 0))
        migrated["state"]["best_id"] = pop.get("best_id", pop.get("state", {}).get("best_id"))
        migrated["state"]["best_score"] = pop.get("best_score", pop.get("state", {}).get("best_score"))
        migrated["state"]["best_genome"] = pop.get("best_genome", pop.get("state", {}).get("best_genome"))
        pop = migrated
        # NORMALIZE: tolerate missing state / mismatched genome_template
        if "config" not in pop or not isinstance(pop.get("config"), dict):
            pop["config"] = {}
        if "state" not in pop or not isinstance(pop.get("state"), dict):
            pop["state"] = {"generation": 0, "best_id": None, "best_score": None, "best_genome": None, "history": []}

        # fold legacy top-level history into state.history when needed
        if isinstance(pop.get("history"), list) and not pop["state"].get("history"):
            pop["state"]["history"] = pop.get("history")

        # ensure genome_template is operator-valid for mutation (alpha/beta/mut_rate)
        gt = pop.get("config", {}).get("genome_template")
        if (not isinstance(gt, dict)) or (not all(k in gt for k in ("alpha", "beta", "mut_rate"))):
            pop["config"]["genome_template"] = {"alpha": 0.50, "beta": 0.50, "mut_rate": 0.05}

        # ensure best_genome exists (needed for Mode C/D)
        if pop["state"].get("best_genome") is None:
            pop["state"]["best_genome"] = dict(pop["config"].get("genome_template", {"alpha":0.5,"beta":0.5,"mut_rate":0.05}))

    # enforce config override inputs (caller wins)
    pop["config"]["pop_size"] = int(pop_size)
    pop["config"]["generations"] = int(generations)
    pop["config"]["steps"] = int(steps)
    pop["config"]["watchdog_seconds"] = int(watchdog)

    return pop

def _persist_population(pop):
    POP_FILE.write_text(json.dumps(pop, indent=2), encoding="utf-8")
    _p("[PERSIST] population.json updated")

def _drain_process(proc: subprocess.Popen, watchdog_seconds: int, tag: str):
    last = time.time()
    while True:
        line = proc.stdout.readline() if proc.stdout else ""
        if line:
            last = time.time()
            _p(f"[{tag}] " + line.rstrip())
        if proc.poll() is not None:
            break
        if (time.time() - last) > watchdog_seconds:
            _p(f"[WATCHDOG] {tag} no output for {watchdog_seconds}s — killing")
            try:
                proc.kill()
            except Exception:
                pass
            break
        time.sleep(0.01)

def _selftest():
    _p("[SELFTEST] probing loop...")
    p = subprocess.run(
        [sys.executable, "-u", str(LOOP), "--selftest", "--workdir", str(RUNS / "_selftest")],
        capture_output=True, text=True
    )
    if p.stdout:
        for ln in p.stdout.splitlines():
            _p(ln)
    if "[SELFTEST] True" not in (p.stdout or ""):
        _fatal("SELFTEST FAILED")
    _p("[SELFTEST] PASS")

def _spawn_worker(i: int, steps: int):
    wd = RUNS / f"organism_{i}"
    wd.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        [sys.executable, "-u", str(LOOP), "--steps", str(steps), "--workdir", str(wd), "--id", str(i)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

def _read_result(i: int):
    wd = RUNS / f"organism_{i}"
    rp = wd / "result.json"
    if not rp.exists():
        return None
    try:
        return json.loads(rp.read_text(encoding="utf-8"))
    except Exception:
        return None

def _mutate_genome(g):
    # Mode C/D: simple bounded mutation of alpha/beta; keeps sum ~1
    mut = float(g.get("mut_rate", 0.05))
    a = float(g.get("alpha", 0.5))
    b = float(g.get("beta", 0.5))
    da = random.uniform(-mut, mut)
    a2 = min(1.0, max(0.0, a + da))
    b2 = min(1.0, max(0.0, 1.0 - a2))
    return {"alpha": a2, "beta": b2, "mut_rate": mut}

def _mode_A(pop):
    cfg = pop["config"]
    _p("DIGITAL-DNA SUPERVISOR (MODE A — SINGLE ORGANISM)")
    _p(f"ROOT: {ROOT}")
    _p(f"STEPS: {cfg['steps']}")
    _p(f"WATCHDOG: {cfg['watchdog_seconds']}")
    _p(f"BOOTLOG: {BOOTLOG}")
    _p("")
    _selftest()
    _p("[RUN] single organism 0")
    p = _spawn_worker(0, int(cfg["steps"]))
    _drain_process(p, int(cfg["watchdog_seconds"]), "ORG0")
    res = _read_result(0) or {"organism_id": 0, "score": None}
    _p(f"[DONE] score={res.get('score')}")
    return 0

def _mode_B(pop, allow_mutation=False, autonomous=False):
    cfg = pop["config"]
    st = pop["state"]

    label = "MODE B" if not allow_mutation else ("MODE C" if not autonomous else "MODE D")
    _p(f"DIGITAL-DNA SUPERVISOR ({label} ECOSYSTEM)")
    _p(f"ROOT: {ROOT}")
    _p(f"POP_FILE: {POP_FILE}")
    _p(f"POP_SIZE: {cfg['pop_size']}")
    _p(f"GENERATIONS: {cfg['generations']}")
    _p(f"STEPS: {cfg['steps']}")
    _p(f"WATCHDOG: {cfg['watchdog_seconds']}")
    _p(f"BOOTLOG: {BOOTLOG}")
    _p("")

    _selftest()

    start_gen = int(st.get("generation", 0))
    G = int(cfg["generations"])
    N = int(cfg["pop_size"])
    steps = int(cfg["steps"])
    WD = int(cfg["watchdog_seconds"])

    # Ensure best genome exists (for C/D)
    if st.get("best_genome") is None:
        st["best_genome"] = dict(cfg.get("genome_template", {"alpha":0.5,"beta":0.5,"mut_rate":0.05}))

    gen = start_gen
    while True:
        if not autonomous and gen >= G:
            break

        gen += 1
        st["generation"] = gen
        _p(f"\n[GEN] {gen}/{G}" if not autonomous else f"\n[GEN] {gen} (autonomous)")

        procs = []
        for i in range(N):
            _p(f"[SPAWN] organism {i}")
            procs.append(_spawn_worker(i, steps))

        for i, p in enumerate(procs):
            _drain_process(p, WD, f"ORG{i}")

        # select best
        best_id = None
        best_score = -1e18
        for i in range(N):
            r = _read_result(i)
            if not r:
                continue
            s = float(r.get("score", -1e18))
            if s > best_score:
                best_score = s
                best_id = int(r.get("organism_id", i))

        st["best_id"] = best_id
        st["best_score"] = best_score

        # evolve genome (C/D)
        if allow_mutation:
            st["best_genome"] = _mutate_genome(st.get("best_genome") or cfg.get("genome_template") or {})
            # tiny deterministic offset so you can see it changing in the file
            st["best_genome"]["_gen"] = gen

        _p(f"[SELECT] best_id={best_id} best_score={best_score}")
        st["history"].append({"gen": gen, "best_id": best_id, "best_score": best_score, "best_genome": st.get("best_genome")})

        _persist_population(pop)

        if not autonomous and gen >= G:
            break

        # MODE D pacing (prevents tight loop)
        if autonomous:
            time.sleep(0.5)

    return 0

def main(argv=None):
    argv = argv or sys.argv[1:]

    # read MODE from env or args (args wins)
    mode = os.environ.get("DDNA_MODE", "B").strip().upper()
    # allow: python -m engine.ecosystem.supervisor --mode D
    if "--mode" in argv:
        try:
            mode = argv[argv.index("--mode") + 1].strip().upper()
        except Exception:
            pass

    # allow overrides
    def _get_int(flag, default):
        if flag in argv:
            try:
                return int(argv[argv.index(flag)+1])
            except Exception:
                return default
        return default

    pop_size = _get_int("--pop", 4)
    generations = _get_int("--gens", 50)
    steps = _get_int("--steps", 200)
    watchdog = _get_int("--wd", 60)

    os.chdir(ROOT)

    pop = _load_or_migrate_population(pop_size, generations, steps, watchdog)

    if mode == "A":
        return _mode_A(pop)
    if mode == "B":
        return _mode_B(pop, allow_mutation=False, autonomous=False)
    if mode == "C":
        return _mode_B(pop, allow_mutation=True, autonomous=False)
    if mode == "D":
        return _mode_B(pop, allow_mutation=True, autonomous=True)

    _fatal(f"Unknown mode '{mode}' (expected A/B/C/D)")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())


