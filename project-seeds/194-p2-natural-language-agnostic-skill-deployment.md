# Seed 194: Explicit Skill Deployment Skills (`deploy-userspace-skills` / `deploy-workspace-skills` / `deploy-skills`)

Priority: P2
Repo: axolync-agent

## Summary

Add three explicit deployment skills instead of one flag-driven skill:

- `deploy-userspace-skills` — deploys `skills-user/` into the running agent's userspace skill directory.
- `deploy-workspace-skills` — deploys `skills-workspace/` into the target workspace's skill directory.
- `deploy-skills` — umbrella that runs both, delegating rather than reimplementing.

All three are authored Codex-first (`$name`) and claudified to `/name`. The same procedures are documented in the README as a natural-language flow, so an agent can perform a deployment by reading the README *before* any of these skills is installed — a pre-skill bootstrap that becomes a real skill once deployed.

## Product Context

Redeploying skills to a new machine or project is currently manual, and there is a bootstrap hole: nothing can be deployed until something is already deployed. `claudify` already owns one axis — transforming the Codex `$name` sources into the Claude shape — but it is not a deployment entry point, and there is no path that installs userspace skills for whichever agent is running.

Explicit, separately named skills are preferred over a single skill with a scope flag: the names are self-describing, discoverable in `$`/`/` autocomplete, and each one states its own blast radius, which matters because userspace and workspace deployments have different targets and different consequences. The umbrella exists so the common "set everything up" case stays one invocation.

## Technical Constraints

- Three skills as named above. `deploy-skills` must delegate to the other two and must not duplicate their logic.
- Each skill is authored Codex-first as `$name` (source of truth) and claudified to `/name`.
- Each deploys for the agent currently running: Codex to the Codex skill directory, Claude to the Claude skill directory. Detect the running agent rather than asking.
- `claudify` is used to produce the Claude shape when the running agent is Claude. `claudify` generates both userspace and workspace copies, so each deploy skill installs only the claudify output relevant to its own scope.
- Deploy whole buckets, never individual skill folders: skills reference each other by sibling-relative script paths (for example `enqueue` invokes `queue-status`'s script), so a partial copy breaks at runtime.
- The README procedure and the installed skills must produce the same result, so an agent that bootstraps cold ends up in the same state as one that runs the skill.
- The Codex `$name` sources remain the single source of truth; deployment never edits them.
- Do not write outside the resolved target directory unless the user explicitly asks.

## Open Questions

- Should `deploy-skills` accept a scope override, or always do both? Recommended: always both; use the specific skill when a narrower scope is wanted.
- On redeploy, overwrite existing skill folders idempotently or skip when present? Recommended: overwrite idempotently, since the repo is the source of truth.
