# Patch Backups Overview

The `_patch_backups/` folder stores point-in-time backup copies made before patching scripts/config.

## Mini Directory
- timestamped folders containing `*.bak` file backups.

## Sequence of Events
1. Backup snapshot is created before mutation/patch operation.
2. Operation proceeds against live files.
3. Backup remains available for manual recovery.

## Interlinking Notes
- Recovery-only scope.
- Do not wire backup files into runtime imports or entrypoints.
