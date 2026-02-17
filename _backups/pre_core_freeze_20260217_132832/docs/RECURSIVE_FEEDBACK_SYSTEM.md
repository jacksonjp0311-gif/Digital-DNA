# DDNA Recursive Feedback System (Codex Integration)

## Purpose
Create a repeatable, explicit feedback loop so every Codex iteration makes measurable improvements with continuity and coherence.

## Loop Contract
1. **Observe**
   - Run deterministic checks.
   - Capture runtime/test artifacts.
   - Record failures, drift changes, and architecture gaps.
2. **Evaluate**
   - Update `ARCHITECTURE_EVALUATION.md` with current findings.
   - Classify findings: correctness, reliability, observability, integration.
3. **Plan**
   - Create one iteration note from template in `feedback/iterations/`.
   - Prioritize high-leverage fixes first.
4. **Implement**
   - Apply scoped code/doc changes linked to findings.
5. **Validate**
   - Re-run command suite and capture pass/fail.
6. **Commit Continuity**
   - Append a dated entry in `CODEX_UPGRADE_LOG.md`.
   - Include next actions.

## Required Artifacts Per Iteration
- `docs/feedback/iterations/YYYY-MM-DD_iteration_<n>.md`
- Updated `docs/CODEX_UPGRADE_LOG.md`
- Updated `docs/ARCHITECTURE_EVALUATION.md` (if architecture conclusions changed)

## Quality Gates
- Stability invariant holds (`S = C - D`).
- Drift clamp invariant holds (`D = clamp(drift_raw, 0, 1)`).
- Baseline policy is explicit (lock vs initialize).
- Configuration validation is explicit and deterministic.

## Codex Execution Guidance
- Every change should map to one or more findings in evaluation docs.
- Avoid disconnected edits; ensure interlinking updates are included.
- Always include follow-up actions so the next iteration starts with context.
