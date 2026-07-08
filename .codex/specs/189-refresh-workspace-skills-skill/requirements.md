# Requirements

## Introduction

This spec implements seed `189-p1-refresh-workspace-skills-skill.md`: a workspace skill that updates `axolync-agent` from latest master and applies/verifies workspace skill exposure for the current workspace without touching user-profile skills.

## Requirements

### Requirement 1: Workspace Skill Placement

**User Story:** As an Axolync maintainer, I want `$refresh-workspace-skills` to be a workspace skill, so agents can repair workspace skill availability without installing user homedir skills.

#### Acceptance Criteria

1. WHEN the skill is implemented THEN it SHALL live under `skills-workspace/refresh-workspace-skills`.
2. WHEN the skill is implemented THEN it SHALL NOT create or modify `~/.codex/skills`.
3. WHEN the skill is listed by `$lssa` THEN `refresh-workspace-skills` SHALL appear under `skills-workspace`.
4. The skill frontmatter SHALL use name `refresh-workspace-skills`.

### Requirement 2: Agent Repo Update Safety

**User Story:** As a maintainer, I want the skill to update from latest agent master without overwriting local work.

#### Acceptance Criteria

1. WHEN the skill starts THEN it SHALL locate the `axolync-agent` repo.
2. WHEN the `axolync-agent` worktree is dirty THEN it SHALL stop and report before pulling.
3. WHEN the worktree is clean THEN it SHALL pull latest `origin/master` using fast-forward-only behavior.
4. WHEN pulling fails THEN it SHALL report the exact blocker.

### Requirement 3: Workspace Skill Exposure Repair

**User Story:** As a workspace user, I want latest tracked workspace skills exposed in the current workspace.

#### Acceptance Criteria

1. WHEN the skill runs THEN it SHALL locate the current workspace root.
2. WHEN `<workspace>/.codex/skills` is missing, stale, copied, or linked incorrectly THEN it SHALL report the state.
3. WHEN repair is safe THEN it SHALL apply the existing Axolync bootstrap convention for workspace skills.
4. WHEN local workspace skill files are dirty or would be overwritten THEN it SHALL stop and report.
5. The skill SHALL NOT mutate user homedir skills.

### Requirement 4: Verification And Runtime Honesty

**User Story:** As a user, I want to know whether skills are visible on disk and whether the current Codex thread can actually use them.

#### Acceptance Criteria

1. WHEN workspace skills are applied THEN the skill SHALL list skills visible from the filesystem.
2. WHEN comparing against `axolync-agent/skills-workspace` THEN it SHALL report missing or extra workspace skills.
3. WHEN the active Codex runtime cannot dynamically reload newly added skill metadata THEN it SHALL state that a new Codex session is required.
4. WHEN a supported runtime refresh mechanism exists THEN the skill MAY use it and report the result.
5. The skill SHALL NOT claim current-session skill availability unless it is actually true.

### Requirement 5: Validation

**User Story:** As a maintainer, I want regression coverage for the skill instructions, so future edits do not weaken safety.

#### Acceptance Criteria

1. Tests SHALL verify the skill exists and has valid frontmatter.
2. Tests SHALL verify it forbids homedir skill mutation.
3. Tests SHALL verify it requires dirty-state refusal before pulling/repair.
4. Tests SHALL verify it includes the current-session reload caveat.
5. `$lssa` SHALL list the new skill.

