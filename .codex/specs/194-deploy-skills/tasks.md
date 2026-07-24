# Tasks - Explicit Skill Deployment Skills

Derived from `requirements.md` and `design.md` in this spec folder.

- [x] 1. Add `skills-user/deploy-userspace-skills/SKILL.md`: detect the running agent; deploy the whole `skills-user/` bucket (Codex: copy Codex-shape folders into the user Codex skills directory; Claude: run `scripts/claudify.py` and install the user-scope output into the user Claude skills directory); idempotent overwrite; never edit sources.
- [x] 2. Add `skills-user/deploy-workspace-skills/SKILL.md`: expose `skills-workspace/` to the current workspace (Codex: README junction rules, create only when absent; Claude: claudify workspace-scope output into the workspace `.claude\skills`).
- [x] 3. Add `skills-user/deploy-skills/SKILL.md`: umbrella that invokes `$deploy-userspace-skills` then `$deploy-workspace-skills`, always both, delegating with no logic of its own.
- [ ] 4. Add a `## Deploying Skills` section near the top of `README.md` prominently naming the three skills, linking their SKILL.md files, and stating the cold-bootstrap property (procedure works by reading before the skills are installed).
