# Seed 194: Natural-Language Agnostic Skill Deployment via README Phrase

Priority: P2
Repo: axolync-agent

## Summary

Add a README-documented natural-language flow: when the user says a canonical phrase (e.g. "deploy skills agnostically to the project"), the currently running agent (Claude or Codex) installs the agent's userspace pipeline skills into the correct skill directory for whichever agent is running — with no separate installer binary.

## Product Context

Redeploying the reusable pipeline skills (`skills-user/`) to a new project currently requires manual junctioning and/or running claudify. The user wants a zero-extra-tooling flow driven entirely from the README: read a documented trigger phrase, and the AI deploys the agnostic userspace skills for its own runtime — Claude into `.claude/skills`, Codex into `.codex/skills` — scoped to the target project. This makes the agent repo instantly redeployable on a new machine without bootstrapping an axolync-specific sibling system.

## Technical Constraints

- Document a canonical trigger phrase and the exact deployment procedure in the agent README (and/or a dedicated bootstrap doc).
- The procedure must detect the running agent (Claude vs Codex) and deploy the `skills-user/` skills into that agent's skill directory in the target project only.
- Reuse existing mechanisms: `scripts/claudify.py` for the Claude shape; junction/copy for the Codex shape. No new compiled installer binary.
- Deploy only `skills-user/` (the agnostic core) by default, not `skills-workspace/` (axolync-specific), unless explicitly asked.
- Must not write into user-global skill directories unless the user explicitly asks; default scope is the target project/workspace.
- Preserve the existing Codex `$name` sources as the single source of truth.

## Open Questions

- Should the phrase deploy both agent shapes (Claude + Codex) or only the running agent's shape? Recommended: only the running agent's shape by default, with an option to do both.
- Is a tiny helper script acceptable as optional backing for the NL steps, or must it be purely natural-language + existing claudify? Recommended: NL steps + reuse claudify; keep any helper optional and thin.
