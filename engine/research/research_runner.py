# engine/research/research_runner.py
# Lightweight experiment queue runner (append-only, non-destructive)
import json, os, time, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RQ = os.path.join(ROOT, "state", "research", "research_queue.jsonl")
RJ = os.path.join(ROOT, "state", "research", "research_journal.jsonl")

def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")

def ensure():
    os.makedirs(os.path.dirname(RQ), exist_ok=True)
    for p in (RQ, RJ):
        if not os.path.exists(p):
            open(p, "a", encoding="utf-8").close()

def journal(kind, payload):
    ensure()
    rec = {"ts": _now(), "kind": kind, "payload": payload}
    with open(RJ, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def pop_one():
    ensure()
    lines = []
    with open(RQ, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    if not lines: return None, []
    head = lines[0]
    rest = lines[1:]
    with open(RQ, "w", encoding="utf-8") as f:
        for ln in rest:
            f.write(ln + "\n")
    return json.loads(head), rest

def run_task(task):
    # task schema: {"name": "...", "cmd": ["python", "-u", "path.py", ...], "timeout_s": 120}
    name = task.get("name","unnamed")
    cmd  = task.get("cmd", [])
    to   = int(task.get("timeout_s", 120))
    if not cmd:
        journal("task_error", {"name": name, "err": "missing cmd"})
        return 1
    journal("task_start", {"name": name, "cmd": cmd})
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=to, encoding="utf-8", errors="replace")
        journal("task_done", {"name": name, "rc": p.returncode, "stdout_tail": p.stdout[-1200:], "stderr_tail": p.stderr[-1200:]})
        return p.returncode
    except subprocess.TimeoutExpired:
        journal("task_timeout", {"name": name, "timeout_s": to})
        return 124

def main():
    ensure()
    task, _ = pop_one()
    if not task:
        journal("idle", {"msg": "no research tasks"})
        return 0
    rc = run_task(task)
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
