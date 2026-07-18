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
- Claudify script: a single Python script `claudify.py` (Python only, cross-platform; no PowerShell variant, to avoid a second source of truth), run by a `claudify` workspace skill. On each run it regenerates Claude-form hard copies (never a symlink/junction) of both buckets, transforming only known-skill `$name` tokens into `/name`. Workspace skills are regenerated and auto-applied to the workspace `.claude/skills` every run; user skills are regenerated into an untracked output artifact folder under the agent repo and are never auto-installed into the global `~/.claude/skills`.
- The transform must rewrite only invocation tokens that resolve to an actual known skill name. It must never touch other `$` usage: PowerShell `$env:` / `$var`, bash `$1`, regex, or any non-skill `$`.
- Claudify CI test: run the script into a throwaway temp directory, inventory every transformation performed against the original source, classify each transformation, and fail if any transformation is unclassified or over-reaching. The test must also assert the inventory is complete (zero unclassified entries). An unclassified transformation is a legitimate CI failure and a signal to improve the classifier. This test runs in `axolync-agent` GitHub Actions CI.
- Rogue invocation escaping: because Codex sources never intentionally use the Claude `/name` form, any pre-existing invocation-position `/name` for a known skill is stale/rogue. Claudify neutralizes it by inserting one space (`/name` -> `/ name`) before converting `$name` -> `/name`, so it cannot trigger a Claude skill. Escaping is invocation-position only; file paths are untouched. This stays valid until a pure-Claude (already `/name`) skill bucket is ever added, which is not planned.
- Per-file uninventoried allowlist: uninventoried `$`-candidates (documentation placeholders, e.g. `$name` in the claudify skill doc) are allowlisted per file. CI fails when an uninventoried `$`-candidate appears in a file not on its allowlist, surfacing typos or unexpected candidates for human review. Both tests run in the same `axolync-agent` CI.
- Generation vs installation for user skills: claudify may generate Claude-form copies of the entire `skills-user` bucket as an untracked artifact under the agent repo, but must never install them into the global `~/.claude/skills`. Installing user skills globally is a manual human step, done typically once per environment lifetime (revisited only if a new user skill is added). The script recreates the artifact each run; it does not auto-install user skills.

## Proposed Scope

1. Add agent-detection branching to the skills sections of the README and bootstrap docs.
2. Add the claudify transform script (`claudify.py`) and a `claudify` workspace skill that runs it.
3. Add the claudify CI test (temp-dir generation + transformation inventory + zero-unclassified assertion), running in `axolync-agent` GitHub Actions.
4. Add rogue-invocation escaping (`/name` -> `/ name`, invocation-position only) and the per-file uninventoried allowlist test, running in the same `axolync-agent` CI.

## Vocabulary Candidate Additions

- `claudify`: the on-demand generation of Claude-compatible skill copies from the canonical Codex skill sources, hard-copied with a scoped `$name` -> `/name` invocation transform.
- `claudify.py`: the single cross-platform Python script that performs claudify, run by the `claudify` workspace skill.

## Resolved Decisions

- Script and skill name: a single Python script `claudify.py` (no PowerShell variant), run by a `claudify` workspace skill.
- CI location: the claudify transformation-inventory test and the source-skill guardrail test both run in `axolync-agent` GitHub Actions, colocated with the skill sources and the transform.
- User-skill generation vs installation: claudify regenerates Claude-form copies of the entire `skills-user` bucket as an untracked artifact under the agent repo on every run, but never installs them globally. Only `skills-workspace` skills are auto-applied to the live `.claude/skills`. Global install of user skills is a manual, typically once-per-environment human action.
- Rogue `/name` escape representation: insert a single space (`/name` -> `/ name`). It defuses the trigger without adding visual noise, and only applies to invocation-position rogues, never to file paths.
- Uninventoried allowlist is per file (not global), so each file declares its own expected placeholders; anything else is a CI failure.

## Open Questions

- None. All open questions resolved; the seed is ready for s2s.
