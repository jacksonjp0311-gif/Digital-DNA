# Digital-DNA CI Gate

Digital-DNA can run as a structural continuity gate in CI.

## Default Gate

```powershell
ddna gate --format json
```

The command uses `config/policy.json` and exits with:

- `0` when all constraints pass,
- `2` when structural continuity violates policy,
- `1` when the CLI cannot complete.

## Policy File

```json
{
  "min_stability": 0.84,
  "max_drift": 0.2,
  "max_topology_drift": 0.12,
  "max_dependency_drift": 0.15,
  "require_retention": 0.95
}
```

## Explanation

```powershell
ddna explain
```

`explain` reads the latest scan record and prints the policy, pass/fail decision, and any violated constraints.

## Strict Baselines

```powershell
$env:DDNA_BASELINE_LOCK = "1"
ddna gate
```

With baseline lock enabled, missing baselines fail instead of initializing automatically.
