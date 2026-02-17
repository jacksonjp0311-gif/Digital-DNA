import os
import sys
import json
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOOP = ROOT / "engine" / "evolution" / "evolution_loop.py"

ECO = ROOT / "ecosystem"
STATE = ECO / "state"
RUNS = STATE / "runs"
POP_FILE = STATE / "population.json"

LOGS = ROOT / "logs"
BOOTLOG = LOGS / "ecosystem_boot.log"

DEFAULTS = {
    "config": {
        "pop_size": 4,
        "generations": 50,
        "steps": 200,
        "watchdog_seconds": 60,
        "genome_template": {"best": None, "history": []}
    },
    "population": [],
    "history": []
}

def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def _append_log(text: str) -> None:
    LOGS.mkdir(exist_ok=True)
    with open(BOOTLOG, "a", encoding="utf-8") as f:
        f.write(text)

def _load_or_init_pop():
    STATE.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)

    if not POP_FILE.exists():
        pop = DEFAULTS
        # initialize population entries
        n = pop["config"]["pop_size"]
        pop["population"] = [{"id": i, "genome": dict(pop["config"]["genome_template"])} for i in range(n)]
        _write(POP_FILE, pop)
        return pop

    raw = POP_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        pop = DEFAULTS
        n = pop["config"]["pop_size"]
        pop["population"] = [{"id": i, "genome": dict(pop["config"]["genome_template"])} for i in range(n)]
        _write(POP_FILE, pop)
        return pop

    pop = json.loads(raw)

    # schema hardening (prevents KeyError: config)
    if "config" not in pop:
        pop["config"] = DEFAULTS["config"]
    for k, v in DEFAULTS["config"].items():
        pop["config"].setdefault(k, v)

    pop.setdefault("population", [])
    if not pop["population"]:
        n = pop["config"]["pop_size"]
        pop["population"] = [{"id": i, "genome": dict(pop["config"]["genome_template"])} for i in range(n)]

    pop.setdefault("history", [])
    _write(POP_FILE, pop)
    return pop

def _print_banner(pop):
    cfg = pop["config"]
    print("")
    print("DIGITAL-DNA SUPERVISOR (MODE B ECOSYSTEM)")
    print("ROOT:", ROOT)
    print("POP_FILE:", POP_FILE)
    print("POP_SIZE:", cfg["pop_size"])
    print("GENERATIONS:", cfg["generations"])
    print("STEPS:", cfg["steps"])
    print("WATCHDOG:", cfg["watchdog_seconds"])
    print("BOOTLOG:", BOOTLOG)
    print("")

def _selftest(pop):
    print("[SELFTEST] probing loop...")
    _append_log("[SELFTEST] probing loop...\n")

    probe = subprocess.run(
        [sys.executable, "-u", str(LOOP), "--selftest", "--steps", "1", "--workdir", str(RUNS / "_selftest"), "--id", "0"],
        capture_output=True,
        text=True
    )

    out = (probe.stdout or "") + (probe.stderr or "")
    print(out, end="")
    _append_log(out)

    if "[SELFTEST] True" not in out:
        raise RuntimeError("SELFTEST FAILED (expected '[SELFTEST] True')")

    print("[SELFTEST] PASS")
    _append_log("[SELFTEST] PASS\n")

def _spawn_worker(org_id: int, steps: int) -> subprocess.Popen:
    wd = RUNS / f"organism_{org_id}"
    wd.mkdir(parents=True, exist_ok=True)

    print(f"[SPAWN] organism {org_id}")
    _append_log(f"[SPAWN] organism {org_id}\n")

    return subprocess.Popen(
        [sys.executable, "-u", str(LOOP), "--steps", str(steps), "--workdir", str(wd), "--id", str(org_id)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

def _drain_process(proc: subprocess.Popen, watchdog: int, label: str) -> None:
    last = time.time()
    while True:
        line = proc.stdout.readline() if proc.stdout else ""
        if line:
            # keep console readable: prefix with organism label
            msg = f"[{label}] {line.rstrip()}\n"
            print(msg, end="")
            _append_log(msg)
            last = time.time()

        if proc.poll() is not None:
            return

        if (time.time() - last) > watchdog:
            msg = f"\n[WATCHDOG] {label} no output for {watchdog}s — killing\n"
            print(msg, end="")
            _append_log(msg)
            try:
                proc.kill()
            except Exception:
                pass
            return

        time.sleep(0.05)

def _read_result(org_id: int):
    wd = RUNS / f"organism_{org_id}"
    rp = wd / "result.json"
    if not rp.exists():
        return None
    try:
        return json.loads(rp.read_text(encoding="utf-8"))
    except Exception:
        return None

def _select_best(pop):
    scores = []
    for i in range(pop["config"]["pop_size"]):
        r = _read_result(i)
        if r and "score" in r:
            scores.append((float(r["score"]), i))
    if not scores:
        return None
    scores.sort(reverse=True)
    return {"best_score": scores[0][0], "best_id": scores[0][1], "all": scores}

def main(argv=None):
    os.chdir(ROOT)
    pop = _load_or_init_pop()
    _print_banner(pop)
    _selftest(pop)

    cfg = pop["config"]
    N = int(cfg["pop_size"])
    G = int(cfg["generations"])
    STEPS = int(cfg["steps"])
    WD = int(cfg["watchdog_seconds"])

    for gen in range(1, G + 1):
        print("")
        print(f"[GEN] {gen}/{G}")
        _append_log(f"\n[GEN] {gen}/{G}\n")

        procs = [ _spawn_worker(i, STEPS) for i in range(N) ]

        # drain each worker sequentially (keeps deterministic console ordering)
        for i, p in enumerate(procs):
            _drain_process(p, WD, f"ORG{i}")

        sel = _select_best(pop)
        if sel is None:
            print("[SELECT] no results found")
            _append_log("[SELECT] no results found\n")
        else:
            print(f"[SELECT] best_id={sel['best_id']} best_score={sel['best_score']}")
            _append_log(f"[SELECT] best_id={sel['best_id']} best_score={sel['best_score']}\n")

        # persist generation summary
        pop["history"].append({
            "gen": gen,
            "selection": sel,
            "ts": time.time()
        })

        _write(POP_FILE, pop)

        print("[PERSIST] population.json updated")
        _append_log("[PERSIST] population.json updated\n")

    print("\n[DONE] generations complete\n")
    _append_log("\n[DONE] generations complete\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())