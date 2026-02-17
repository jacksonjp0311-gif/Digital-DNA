from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    print("DDNA SAFE BOOT ACTIVE -> delegating to canonical loop entrypoint")
    subprocess.run(
        [sys.executable, "-m", "tools.ddna_loop", "--forever", "--sleep-seconds", "2"],
        cwd=str(ROOT),
        check=True,
    )


if __name__ == "__main__":
    main()
