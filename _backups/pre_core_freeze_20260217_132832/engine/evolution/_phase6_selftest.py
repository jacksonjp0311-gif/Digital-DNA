import sys
sys.path.insert(0, r"C:\Users\jacks\OneDrive\Desktop\Digital-DNA\engine\evolution")
import evolution_core as core
ok,msg = core.selftest()
print("[SELFTEST]", ok, msg)
sys.exit(0 if ok else 2)