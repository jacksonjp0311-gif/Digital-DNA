import argparse, json, os, shutil, subprocess, time, random
from pathlib import Path

# Keep evo out of recursive self-copy loops and large dirs.
EXCLUDE_DIRS = {
  "_mutations","ddna_evo","DDNA_EVO_SANDBOX",".git","__pycache__",".venv","venv",
  "node_modules","dist","build",".mypy_cache",".pytest_cache"
}

def ignore_func(dirpath, names):
    # dirpath is a string; names are entries inside it
    out = []
    for n in names:
        if n in EXCLUDE_DIRS:
            out.append(n)
    return out

def safe_rmtree(p: Path):
    if not p.exists(): return
    def onerr(func, path, exc):
        try:
            os.chmod(path, 0o700)
            func(path)
        except Exception:
            pass
    shutil.rmtree(p, onerror=onerr)

def copy_repo(src: Path, dst: Path):
    safe_rmtree(dst)
    shutil.copytree(src, dst, ignore=ignore_func)

def read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def write_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def mutate_json_bump(repo_root: Path, relpath: str, key: str, step: float, stamp: str):
    p = repo_root / relpath
    obj = read_json(p)
    if key not in obj or not isinstance(obj[key], (int, float)):
        raise SystemExit(f"json_bump: key '{key}' missing or not numeric in {p}")
    obj[key] = float(obj[key]) + float(step)
    obj["_evo_stamp"] = stamp
    write_json(p, obj)

def run_ddna(repo_root: Path, entry: str, timeout: int | None):
    cmd = ["python", str(repo_root / entry)]
    p = subprocess.Popen(
        cmd, cwd=str(repo_root),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True
    )
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        return None, out, "TIMEOUT\n" + err

    last = repo_root / "artifacts" / "last_run.json"
    stab = None
    if last.exists():
        try:
            stab = json.loads(last.read_text(encoding="utf-8")).get("stability")
        except Exception:
            stab = None
    return stab, out, err

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orig", required=True)
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("--entry", required=True)
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--timeout", type=int, default=600)

    # Mutation target (REAL knobs)
    ap.add_argument("--mutate", required=True, help="relative json path inside repo to mutate")
    ap.add_argument("--json-key", required=True)
    ap.add_argument("--json-step", type=float, default=0.01)

    # Optional: randomize step sign each trial
    ap.add_argument("--random-sign", action="store_true")

    args = ap.parse_args()

    orig = Path(args.orig).resolve()
    sandbox = Path(args.sandbox).resolve()
    stamp = time.strftime("%Y%m%d_%H%M%S")

    run_root = sandbox / ("run_" + stamp)
    base = run_root / "baseline"
    trials_dir = run_root / "trials"
    trials_dir.mkdir(parents=True, exist_ok=True)

    print("Baseline copy...")
    copy_repo(orig, base)
    baseS, _, _ = run_ddna(base, args.entry, args.timeout)
    print("Baseline stability:", baseS)

    best = baseS
    best_trial = None

    report = {
        "stamp": stamp,
        "orig": str(orig),
        "sandbox": str(sandbox),
        "entry": args.entry,
        "baseline_stability": baseS,
        "mutate": args.mutate,
        "json_key": args.json_key,
        "json_step": args.json_step,
        "trials": []
    }

    for i in range(args.trials):
        tstamp = f"{stamp}_t{i:02d}"
        tdir = trials_dir / f"t{i:02d}"
        copy_repo(orig, tdir)

        step = float(args.json_step)
        if args.random_sign and (random.random() < 0.5):
            step = -step

        mutate_json_bump(tdir, args.mutate, args.json_key, step, tstamp)
        stab, out, err = run_ddna(tdir, args.entry, args.timeout)

        print("trial", i, "step", step, "stability", stab)

        report["trials"].append({
            "i": i,
            "step": step,
            "stability": stab,
            "trial_dir": str(tdir),
        })

        if (stab is not None) and (best is not None) and (stab > best):
            best = stab
            best_trial = i

    report["best_stability"] = best
    report["best_trial"] = best_trial

    report_path = run_root / "evo_report.json"
    write_json(report_path, report)

    print("BEST:", best, best_trial)
    print("REPORT:", str(report_path))

if __name__ == "__main__":
    main()



