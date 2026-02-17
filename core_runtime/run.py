import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / "engine"

sys.path.append(str(ENGINE))
sys.path.append(str(ENGINE / "ecosystem"))
sys.path.append(str(ENGINE / "evolution"))

from ecosystem import supervisor

if __name__ == "__main__":
    supervisor.main()
