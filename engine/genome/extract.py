import hashlib
import os

ENGINE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

def extract_genome():
    signatures = set()

    for root, dirs, files in os.walk(ENGINE_ROOT):
        for f in files:
            if f.endswith(".py"):
                full = os.path.join(root, f)
                with open(full, "rb") as fh:
                    signatures.add(
                        hashlib.sha256(fh.read()).hexdigest()
                    )

    return sorted(signatures)
