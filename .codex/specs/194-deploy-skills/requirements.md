# Requirements - Explicit Skill Deployment Skills

Derived from seed 194 (`project-seeds/194-p2-natural-language-agnostic-skill-deployment.md`).

## R1. Three explicit deployment skills exist
`skills-user/` contains `deploy-userspace-skills`, `deploy-workspace-skills`, and `deploy-skills`, each a Codex-first `$name` skill (claudified to `/name` by the existing claudify flow).

## R2. deploy-userspace-skills deploys the userspace bucket for the running agent
It detects the running agent and deploys the whole `skills-user/` bucket: Codex copies the Codex-shape sources into the user Codex skills directory; Claude generates the Claude shape via `scripts/claudify.py` and installs the user-scope output into the user Claude skills directory. Never a partial bucket.

## R3. deploy-workspace-skills deploys the workspace bucket for the running agent
It exposes `skills-workspace/` to the current workspace: Codex via the workspace `.codex\skills` junction (creating it only when absent, per the existing README junction rules); Claude via claudify's workspace-scope output into the workspace `.claude\skills`.

## R4. deploy-skills is a pure umbrella
It runs `deploy-userspace-skills` then `deploy-workspace-skills`, always both scopes, delegating without duplicating their logic.

## R5. Redeploy is idempotent overwrite
Existing deployed skill folders are overwritten from the repo state on redeploy; the Codex `$name` sources are never edited by deployment.

## R6. README-bootstrappable
The README prominently references the three skills and their procedure near the top, findable and executable by a cold agent reading the repo before any skill is installed, and producing the same result as running the installed skills.

## R7. Scope safety
No skill writes outside its resolved target (user skills directory or workspace skills directory) unless the user explicitly asks.
