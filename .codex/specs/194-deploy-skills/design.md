# Design - Explicit Skill Deployment Skills

Derived from `requirements.md` and seed 194.

## Shape

Three instruction-only skills (no new scripts, no installer binary) under `skills-user/`:

- `deploy-userspace-skills/SKILL.md`
- `deploy-workspace-skills/SKILL.md`
- `deploy-skills/SKILL.md`

Each is a natural-language procedure the running agent executes with its normal tools, reusing the existing mechanisms: direct folder copy for the Codex shape, `scripts/claudify.py` for the Claude shape (claudify already generates both user-scope and workspace-scope outputs; each skill installs only the output relevant to its scope).

## Agent detection

The running agent knows what it is: Codex sessions deploy the Codex shape to the user Codex skills directory; Claude sessions run claudify and deploy the Claude shape to the user Claude skills directory. No flag, no prompt.

## Procedures

- Userspace (Codex): for each folder in `<agent-repo>/skills-user/`, copy it into the user Codex skills directory, replacing any existing folder of the same name. Whole bucket, never a subset (skills reference sibling skills by relative script paths, e.g. `enqueue` invokes `queue-status`'s script).
- Userspace (Claude): run `python scripts/claudify.py`; install the generated user-scope skill folders into the user Claude skills directory, replacing existing same-name folders.
- Workspace (Codex): follow the README junction rules — create `<workspace>\.codex\skills` -> `<agent-repo>\skills-workspace` only when the path is absent; if it exists, inspect and ask before replacing.
- Workspace (Claude): run `python scripts/claudify.py`; it installs the workspace-scope output into `<workspace>\.claude\skills` (its existing behavior).
- Umbrella: invoke the userspace skill, then the workspace skill; report both results; add no logic of its own.

## Idempotency and safety

- Overwrite deployed copies from repo state (repo is the source of truth); never edit `skills-user/` sources.
- New skills surface in `$`/`/` autocomplete only in sessions started after deployment; the procedures say so.
- No writes outside the resolved targets.

## README

A `## Deploying Skills` section placed directly after the reading-order line at the top of the README, naming the three skills, stating the cold-bootstrap property (readable and executable before installation), and linking the skill files.
