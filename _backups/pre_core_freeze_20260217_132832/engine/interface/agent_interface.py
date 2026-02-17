# engine/interface/agent_interface.py
# Minimal “human ↔ system” interface layer (file-based, append-only)
import json, os, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INBOX  = os.path.join(ROOT, "state", "interface", "inbox.jsonl")
OUTBOX = os.path.join(ROOT, "state", "interface", "outbox.jsonl")
GOALS  = os.path.join(ROOT, "state", "interface", "goals.json")
PROG   = os.path.join(ROOT, "state", "interface", "progress.json")
EVAL   = os.path.join(ROOT, "state", "interface", "evaluation.jsonl")

def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")

def ensure_files():
    os.makedirs(os.path.dirname(INBOX), exist_ok=True)
    for p in (INBOX, OUTBOX, EVAL):
        if not os.path.exists(p):
            open(p, "a", encoding="utf-8").close()
    if not os.path.exists(GOALS):
        with open(GOALS, "w", encoding="utf-8") as f:
            json.dump({"goals": [], "active_goal": None, "created": _now()}, f, indent=2)
    if not os.path.exists(PROG):
        with open(PROG, "w", encoding="utf-8") as f:
            json.dump({"last_update": _now(), "loop_iters": 0, "best_raw": None, "best_conf": None}, f, indent=2)

def post_outbox(kind, payload):
    ensure_files()
    rec = {"ts": _now(), "kind": kind, "payload": payload}
    with open(OUTBOX, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def load_goals():
    ensure_files()
    with open(GOALS, "r", encoding="utf-8") as f:
        return json.load(f)

def set_active_goal(goal_text):
    g = load_goals()
    g["active_goal"] = goal_text
    if goal_text and goal_text not in g["goals"]:
        g["goals"].append(goal_text)
    with open(GOALS, "w", encoding="utf-8") as f:
        json.dump(g, f, indent=2, ensure_ascii=False)
    post_outbox("goal_set", {"active_goal": goal_text})

def update_progress(loop_iters=None, best_raw=None, best_conf=None):
    ensure_files()
    with open(PROG, "r", encoding="utf-8") as f:
        p = json.load(f)
    p["last_update"] = _now()
    if loop_iters is not None: p["loop_iters"] = int(loop_iters)
    if best_raw is not None: p["best_raw"] = float(best_raw)
    if best_conf is not None: p["best_conf"] = float(best_conf)
    with open(PROG, "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2, ensure_ascii=False)

def append_eval(score, notes, snapshot=None):
    ensure_files()
    rec = {"ts": _now(), "score": score, "notes": notes, "snapshot": snapshot or {}}
    with open(EVAL, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    ensure_files()
    post_outbox("interface_online", {"root": ROOT})
