# 191 - P1 Claudify Cross-Agent Skills

## Summary

Add a "claudify" pathway so Axolync agent skills work under Claude Code as well as Codex. Keep the Codex-style skill sources as the single source of truth, and generate Claude-compatible copies on demand with a scoped transform, guarded by CI.

## Product Context

Today the skills layer assumes Codex only:

- Skills are exposed by junctioning `<workspace>\.codex\skills` to `axolync-agent/skills-workspace`.
- Skills invoke each other with the Codex `$name` prefix.

Claude Code uses a different skills folder (`.claude/skills`) and a different invocation character (`/name`). Because a symlink/junction would share the same files, the `$` invocation cannot simply be reused for Claude. The chosen approach is to keep the Codex sources canonical and produce transformed hard copies for Claude, never a shared link.

## Technical Constraints

- Cross-agent bootstrap docs: detect which agent is bootstrapping, then use `.codex/skills` + `$name` for Codex, or `.claude/skills` + `/name` for Claude. Update the README and bootstrap docs to branch on this instead of hardcoding the Codex recipe.
- Claudify script: a single Python script `claudify.py` (Python only, cross-platform; no PowerShell variant, to avoid a second source of truth), run by a `claudify` workspace skill. It hard-copies (not symlink/junction) `skills-workspace` (and any explicitly named `skills-user` skill) into `.claude/skills`, transforming only known-skill `$name` tokens into `/name`.
- The transform must rewrite only invocation tokens that resolve to an actual known skill name. It must never touch other `$` usage: PowerShell `$env:` / `$var`, bash `$1`, regex, or any non-skill `$`.
- Claudify CI test: run the script into a throwaway temp directory, inventory every transformation performed against the original source, classify each transformation, and fail if any transformation is unclassified or over-reaching. The test must also assert the inventory is complete (zero unclassified entries). An unclassified transformation is a legitimate CI failure and a signal to improve the classifier. This test runs in `axolync-agent` GitHub Actions CI.
- Source-skill guardrail test: tracked source skills may use only the canonical `$` prefix for cross-skill calls. The `/`-style invocation must never appear in tracked sources; it may exist only in generated Claude copies. This test runs in the same `axolync-agent` CI.
- Do not install anything into the user-level Claude skills directory except on explicit per-named-skill request, mirroring the existing Codex user-skill policy.

## Proposed Scope

1. Add agent-detection branching to the skills sections of the README and bootstrap docs.
2. Add the claudify transform script (`claudify.py`) and a `claudify` workspace skill that runs it.
3. Add the claudify CI test (temp-dir generation + transformation inventory + zero-unclassified assertion), running in `axolync-agent` GitHub Actions.
4. Add the source-skill single-prefix guardrail test, running in the same `axolync-agent` CI.

## Vocabulary Candidate Additions

- `claudify`: the on-demand generation of Claude-compatible skill copies from the canonical Codex skill sources, hard-copied with a scoped `$name` -> `/name` invocation transform.
- `claudify.py`: the single cross-platform Python script that performs claudify, run by the `claudify` workspace skill.

## Resolved Decisions

- Script and skill name: a single Python script `claudify.py` (no PowerShell variant), run by a `claudify` workspace skill.
- CI location: the claudify transformation-inventory test and the source-skill guardrail test both run in `axolync-agent` GitHub Actions, colocated with the skill sources and the transform.

## Open Questions

- When claudify processes the `skills-user` bucket, must it generate a Claude copy only for skills named explicitly, one at a time (never converting the whole user bucket at once) — the same way the Codex bootstrap policy forbids bulk-installing user skills? The `skills-workspace` bucket is always claudified in bulk; this question is only about the `skills-user` bucket.
