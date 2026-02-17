import time, sys
from evolution_core import step_once

# This line is intentionally self-written by the engine (grammar-safe):
MUT_SCALE = 0.933459

print("DDNA EVOLUTION ACTIVE (MODE C: CRASH-LEARNING + FREE MUTATION)")

# One step per process run (supervisor restarts on crash)
# This makes crashes containable and learnable.
rc = step_once()
time.sleep(0.15)
sys.exit(rc)