import os
import sys
import time
import subprocess
from pathlib import Path

ROOT = Path(os.environ.get("DDNA_ROOT", Path(__file__).resolve().parent)).resolve()
ENGINE = ROOT / "engine" / "evolution"
LOOP = ENGINE / "evolution_loop.py"

OID = os.environ.get("DDNA_ORGANISM_ID", "0")
RUN_DIR = Path(os.environ.get("DDNA_RUN_DIR", str((ROOT / "ecosystem" / "runs" / f"org_{OID}")))).resolve()

def main() -> int:
    os.chdir(ROOT)
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    if not LOOP.exists():
        print(f"[ORG {OID}] [FATAL] missing evolution_loop.py: {LOOP}")
        return 2

    # Environment hints for evolution loop (non-breaking if loop ignores them)
    env = os.environ.copy()
    env["DDNA_ORGANISM_ID"] = str(OID)
    env["DDNA_RUN_DIR"] = str(RUN_DIR)

    print(f"[ORG {OID}] worker start | run_dir={RUN_DIR}")

    # Execute the loop directly (NOT imported) to avoid import drift.
    # If your loop supports organism ids later, it can read env vars above.
    p = subprocess.Popen(
        [sys.executable, "-u", str(LOOP)],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # Stream everything upward; supervisor watches silence + restarts
    try:
        while True:
            if p.stdout:
                line = p.stdout.readline()
            else:
                line = ""
            if line:
                print(line.rstrip())
            if p.poll() is not None:
                return int(p.returncode or 0)
            time.sleep(0.05)
    except KeyboardInterrupt:
        try:
            p.kill()
        except Exception:
            pass
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
