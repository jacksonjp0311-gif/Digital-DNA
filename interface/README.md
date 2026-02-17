# Interface Overview

The `interface/` folder contains file-based inbox/outbox transport streams.

## Mini Directory
- `inbox.jsonl` — incoming tasks/events.
- `outbox.jsonl` — outgoing responses/events.

## Sequence of Events
1. Producers append incoming messages to inbox.
2. Interface/agent flows process messages.
3. Responses/events are appended to outbox.

## Interlinking Notes
- Files are append-oriented runtime logs.
- Avoid manual edits unless performing controlled recovery.
