# PENdp Codex Audit Workflow

## Pattern
After major code changes (V3→V4 level), run an independent Codex audit:

1. **Write audit brief**: `CODE_AUDIT_BRIEF.md` specifying scope, files, checklist, key questions
2. **Spawn Codex**: `codex exec --sandbox workspace-write "Read CODE_AUDIT_BRIEF.md and audit..."` 
3. **Read report**: Codex outputs `CODE_AUDIT_REPORT.md` with Critical/Warnings/Suggestions/Score
4. **Fix criticals**: Address all Critical issues first, then high-impact Warnings
5. **Regression test**: Run 9-test suite to verify no regressions
6. **Push**: Commit with audit findings summary

## Example (V4 audit)
- Brief: `CODE_AUDIT_BRIEF.md` (5 files, 8-point checklist, 5 key questions)
- Report: `CODE_AUDIT_REPORT.md` — 5 Critical + 9 Warnings + 5 Suggestions, score 5/10
- Fixes applied: all 5 Critical + all 9 Warnings → 9/9 regression tests pass
- Estimated post-fix score: 7-8/10

## Key lessons
- Codex finds real bugs that human review misses (residue counting, state isolation)
- GFW may cause WebSocket failures; Codex retries 5x and often succeeds
- Always verify with `python -m compileall -q` before trusting "it compiled"
- W1 (residue counting) was a V2 bug that affected ALL scoring — never assume legacy code is correct
