import sys, os

SELFTEST = "--selftest" in sys.argv

try:
    import evolution_core as core
    CORE_OK = True
except:
    CORE_OK = False

if SELFTEST:
    print("[SELFTEST] True ok" if CORE_OK else "[SELFTEST] False")
    sys.exit(0)

# Unicode safe console
try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except:
    pass

print("DDNA PHASE 6->7 ACTIVE (MODE C)")
import time, traceback, sys, os
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
  sys.path.insert(0, HERE)

import evolution_core as core

print("DDNA PHASE 6â†’7 ACTIVE (MODE C)")
print("CORE:", getattr(core, "__file__", "(unknown)"))
try:
  ok,msg = core.selftest()
  print("[SELFTEST]", ok, msg)
except Exception as e:
  print("[SELFTEST] failed:", type(e).__name__, str(e))
print("----")

i = 0
while True:
  i += 1
  try:
    if hasattr(core, "restore_last_good_if_needed"):
      core.restore_last_good_if_needed()

    core.step(i)

  except Exception as e:
    msg = " ".join([type(e).__name__, str(e)])
    print("\n[CRASH]", msg)
    traceback.print_exc()

    try:
      if hasattr(core, "crash_learn"):
        core.crash_learn(msg, i)
    except Exception:
      pass

    try:
      if hasattr(core, "restore_last_good_if_needed"):
        core.restore_last_good_if_needed()
    except Exception:
      pass

    print("[RECOVER] sleeping 1s then continue...\n")
    time.sleep(1)

  time.sleep(0.12)
