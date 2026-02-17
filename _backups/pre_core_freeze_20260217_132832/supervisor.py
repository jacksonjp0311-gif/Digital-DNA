# Root shim: keep imports stable, but canonical logic lives in engine/ecosystem/supervisor.py
from engine.ecosystem.supervisor import main

if __name__ == "__main__":
    raise SystemExit(main())