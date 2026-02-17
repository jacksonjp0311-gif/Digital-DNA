from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    print("engine/evolution_loop.py is now a compatibility wrapper.")
    print("Using canonical loop entrypoint: python -m tools.ddna_loop --forever")
    subprocess.run(
        [sys.executable, "-m", "tools.ddna_loop", "--forever", "--sleep-seconds", "0.5"],
        cwd=str(ROOT),
        check=True,
    )


if __name__ == "__main__":
    main()
