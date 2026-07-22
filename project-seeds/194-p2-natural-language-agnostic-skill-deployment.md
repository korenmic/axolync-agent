# Seed 194: `deploy-skills` — Userspace Skill Deployment Skill (README-bootstrappable)

Priority: P2
Repo: axolync-agent

## Summary

Add a skill named `deploy-skills` that deploys this repo's userspace skills (`skills-user/`) into the userspace of whichever agent is currently running. It is authored Codex-first as `$deploy-skills` and claudified to `/deploy-skills`. The same procedure is also documented in the README as a natural-language flow (a canonical trigger phrase), so an agent can perform the deployment by reading the README *before* the skill itself is installed — a pre-skill bootstrap concept that becomes a real skill once deployed.

## Product Context

Redeploying the reusable pipeline skills to a new machine or project is currently manual. `claudify` already covers one axis — transforming the Codex `$name` sources into the Claude shape and installing the *workspace* copies — but there is no single path that installs the *userspace* skills for whichever agent is running. That leaves a bootstrap hole: on a fresh environment nothing can be deployed until something is already deployed.

`deploy-skills` closes that hole from both ends: as a documented README procedure any agent can execute cold, and as an installed skill afterwards. The two mechanisms compose rather than overlap — `claudify` owns the Codex→Claude shape transform and workspace exposure; `deploy-skills` owns userspace deployment and delegates the Claude shape to `claudify` instead of duplicating that logic.

## Technical Constraints

- Skill name is `deploy-skills`, invoked as `$deploy-skills` (Codex source of truth) and `/deploy-skills` after claudify.
- Deploys `skills-user/` only. `skills-workspace/` is out of scope; workspace exposure stays owned by the workspace junction and `claudify`.
- Default target is the userspace of the agent currently running: Codex to the user Codex skills directory, Claude to the user Claude skills directory. Detect the running agent rather than asking.
- Support an explicit opt-in to deploy both agent shapes in one run, but never do both silently by default.
- Reuse `scripts/claudify.py` to produce the Claude shape; do not reimplement the transform.
- Deploy the whole `skills-user/` bucket together, never individual skill folders: skills reference each other by sibling-relative script paths (for example `enqueue` invokes `queue-status`'s script), so a partial copy breaks at runtime.
- The README procedure and the installed skill must produce the same result, so an agent that bootstraps cold ends up in the same state as one that runs the skill.
- The Codex `$name` sources remain the single source of truth; deployment never edits them.
- Do not write outside the resolved userspace target unless the user explicitly asks.

## Open Questions

- May a thin helper script back the natural-language steps, or must the flow stay pure natural language plus the existing `claudify`? Recommended: allow an optional thin helper, but keep the README procedure sufficient on its own.
- On redeploy, should existing skill folders be overwritten idempotently or skipped when present? Recommended: overwrite idempotently, since the repo is the source of truth.
