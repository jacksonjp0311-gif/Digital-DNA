import json
from datetime import datetime

def append_ledger(path, record):
    record['timestamp'] = datetime.utcnow().isoformat()
    with open(path, 'a') as f:
        f.write(json.dumps(record) + '\\n')
