# DIGITAL-DNA — EVOLUTION LOOP (CANONICAL, REPAIRED)
# Purpose: Stable loop runner + hard selftest handshake + crash recovery
# Encoding: UTF-8

import os
import sys
import time
import json
import traceback
import importlib.util
from pathlib import Path

ROOT   = Path(__file__).resolve().parents[2]          # .../Digital-DNA
ENGINE = ROOT / "engine" / "evolution"
COREPY = ENGINE / "evolution_core.py"

def _load_core_module(path: Path):
    spec = importlib.util.spec_from_file_location("ddna_evolution_core", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _build_core(mod):
    # Preferred: factory function
    if hasattr(mod, "build_core") and callable(getattr(mod, "build_core")):
        return mod.build_core()

    # Common class names
    for name in ("EvolutionCore", "EvolutionEngine", "Core", "Engine"):
        if hasattr(mod, name):
            obj = getattr(mod, name)
            if callable(obj):
                try:
                    inst = obj()
                    if hasattr(inst, "step"):
                        return inst
                except Exception:
                    pass

    # Fallback: any callable/class producing .step
    for k, v in vars(mod).items():
        if k.startswith("_"):
            continue
        if callable(v):
            try:
                inst = v()
                if hasattr(inst, "step"):
                    return inst
            except Exception:
                pass

    raise RuntimeError("No compatible core found. Expected build_core() or a class with .step()")

def main():
    os.chdir(ROOT)

    # Hard selftest handshake (run.py expects this)
    if "--selftest" in sys.argv:
        try:
            mod = _load_core_module(COREPY)
            core = _build_core(mod)
            # optional core selftest hook
            if hasattr(core, "selftest"):
                ok = core.selftest()
                # Normalize truthiness
                if ok is False:
                    print("[SELFTEST] False")
                    return 2
            print("[SELFTEST] True ok")
            return 0
        except Exception as e:
            print("[SELFTEST] False", type(e).__name__, str(e))
            traceback.print_exc()
            return 2

    # Normal run
    try:
        mod = _load_core_module(COREPY)
        core = _build_core(mod)
    except Exception as e:
        print("[BOOT] core load failed:", type(e).__name__, str(e))
        traceback.print_exc()
        return 2

    i = 0
    while True:
        try:
            i += 1
            core.step(i)
        except KeyboardInterrupt:
            print("\n[STOP] KeyboardInterrupt\n")
            return 0
        except Exception as e:
            msg = " ".join([type(e).__name__, str(e)])
            print("\n[CRASH]", msg)
            traceback.print_exc()

            # Optional learning hooks (non-fatal)
            if hasattr(core, "crash_learn"):
                try:
                    core.crash_learn(msg, i)
                except Exception:
                    pass

            # Optional rollback hook (non-fatal)
            if hasattr(core, "restore_last_good_if_needed"):
                try:
                    core.restore_last_good_if_needed()
                except Exception:
                    pass

            print("[RECOVER] sleeping 1s then continue...\n")
            time.sleep(1)

        time.sleep(0.12)

if __name__ == "__main__":
    raise SystemExit(main())
