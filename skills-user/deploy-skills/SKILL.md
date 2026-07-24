---
name: deploy-skills
description: Deploy both skill scopes for the running agent by delegating to deploy-userspace-skills and then deploy-workspace-skills. Use when invoked as $deploy-skills or when the user asks to set up or refresh all skills on a machine or workspace.
---

# Deploy Skills

Umbrella skill. Always both scopes, always by delegation, no logic of its own.

## Procedure

1. Run the `$deploy-userspace-skills` procedure to completion.
2. Run the `$deploy-workspace-skills` procedure to completion.
3. Report both results together (deployed skill names + targets, exposure mechanism + workspace path).

Rules:

- Always deploy both scopes. When a narrower scope is wanted, invoke the specific skill directly instead of this one.
- Delegate; do not restate or fork the scoped skills' rules. Their rules (whole-bucket, idempotent overwrite, junction safety, no source edits, scope safety) apply unchanged.
- If the userspace step fails, still attempt the workspace step, then report both outcomes honestly.
