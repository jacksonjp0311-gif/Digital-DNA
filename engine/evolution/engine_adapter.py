import os, re, subprocess, json, time

def run_baseline(engine_path: str, cwd: str, timeout_s: int = 60) -> float:
    """
    Executes run_ddna.py and extracts the last 'STABILITY:' float from stdout.
    Never edits engine. Returns -999999 on any failure.
    """
    try:
        p = subprocess.run(
            ["python", engine_path],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s
        )
        out = (p.stdout or "") + "\n" + (p.stderr or "")
        vals = []
        for line in out.splitlines():
            if "STABILITY:" in line:
                m = re.search(r"STABILITY:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", line)
                if m:
                    vals.append(float(m.group(1)))
        if vals:
            return float(vals[-1])
        return -999999.0
    except Exception:
        return -999999.0
