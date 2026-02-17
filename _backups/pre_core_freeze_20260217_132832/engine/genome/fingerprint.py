import hashlib
import json
from typing import Any, Dict

def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def fingerprint_genome(genome: Dict[str, Any]) -> str:
    """
    Deterministic fingerprint of the genome object.
    This is the canonical structural signature used for retention.
    """
    s = stable_json(genome)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()