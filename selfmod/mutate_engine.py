import json, time, shutil, difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG  = Path(__file__).resolve().parent / "mutation_config.json"
LOGD = Path(__file__).resolve().parent / "logs"
LOGD.mkdir(parents=True, exist_ok=True)

def now():
    return time.strftime("%Y%m%d_%H%M%S")

def load_cfg():
    try:
        txt = CFG.read_text(encoding="utf-8-sig").strip()
        if not txt:
            return {"enabled": False}
        return json.loads(txt)
    except Exception as e:
        print("[SELFMOD] json parse fail:", e)
        return {"enabled": False}

def read_text(p: Path):
    return p.read_text(encoding="utf-8")

def write_text_atomic(p: Path, text: str):
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(p)

def backup(p: Path):
    b = p.with_suffix(p.suffix + ".bak")
    shutil.copy2(p, b)
    return b

def log_json(name, obj):
    out = LOGD / f"{now()}_{name}.json"
    out.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return out

cfg = load_cfg()
print("[SELFMOD] cfg path:", str(CFG))

if not cfg.get("enabled", False):
    print('{"changed": false, "why":"disabled"}')
    raise SystemExit

files = cfg.get("files", [])
if not files:
    print('{"changed": false, "why":"no files"}')
    raise SystemExit

target = ROOT / files[0]
if not target.exists():
    print('{"changed": false, "why":"missing target", "file": str(target)}')
    raise SystemExit

print("[SELFMOD] config OK")
orig = read_text(target)

# --- GOVERNED mutation: tiny safe transform (comment toggle) ---
# We only do a micro-mutation that cannot break syntax:
# append a trailing newline + tagged comment (idempotent)
tag = "# [DDNA_MUTATION_MARK]"
if tag in orig:
    mutated = orig.replace(tag, tag + " ")
else:
    mutated = orig.rstrip() + "\n" + tag + "\n"

if mutated == orig:
    print('{"changed": false, "why":"no-op"}')
    raise SystemExit

diff = "\n".join(difflib.unified_diff(
    orig.splitlines(), mutated.splitlines(),
    fromfile=str(target), tofile=str(target),
    lineterm=""
))

# backup + apply atomically
bak = backup(target)
write_text_atomic(target, mutated)

payload = {
  "changed": True,
  "file": str(target),
  "backup": str(bak),
  "diff_preview": diff[:2000]
}
log_json("proposal", payload)

print(json.dumps({"changed": True}))
