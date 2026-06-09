# Consumed Repo Descriptor Standard Skill Requirements

## Introduction

The `axolync-add-consumed-repo` workspace skill must guide future repo onboarding to the descriptor-owned standard used by the CI-group builder modernization. New repos must not be created with legacy `config/repos.json` command, package, or inventory fallback authority.

## Requirements

### Requirement 1: Descriptor-Owned Repo Surfaces

**User Story:** As an Axolync maintainer, I want the add-consumed-repo skill to require descriptor-owned exports, so new repos do not create descriptor fallback warnings in Builder reports.

#### Acceptance Criteria

1. WHEN the skill instructs an agent to add a new repo THEN it SHALL require `axolync.repo.toml` when descriptor authority applies.
2. WHEN a repo has tests THEN the skill SHALL require descriptor-owned test exports.
3. WHEN a repo produces installable artifacts THEN the skill SHALL require descriptor-owned packaging/generated-output exports.
4. WHEN a repo exposes adapter/catalog inventory THEN the skill SHALL require descriptor-owned inventory exports.
5. WHEN a repo has project seeds or docs that Builder should report THEN the skill SHALL require descriptor-owned docs/project-seed exports.

### Requirement 2: No Legacy Fallback Guidance For New Repos

**User Story:** As an Axolync maintainer, I want the skill to reject old-school fallback metadata for new repos, so agents do not recreate OffGrid-style red warnings.

#### Acceptance Criteria

1. WHEN the skill discusses new repo onboarding THEN it SHALL NOT instruct agents to add repo-owned authority to `config/repos.json`.
2. WHEN the skill lists forbidden fallback fields THEN it SHALL include `buildCommands`, `sanityCommands`, `testCommands`, `addonPackage`, `adapterCatalogManifestPath`, and `adapterCatalogManifestProfileId`.
3. WHEN builder config is still needed THEN the skill SHALL limit it to builder-owned discovery data such as path, URL, version, and cleaning/bootstrap hints.
4. WHEN legacy fallback exists in an older repo THEN the skill SHALL frame it as modernization debt, not as a pattern to copy.

### Requirement 3: Builder Warning Proof

**User Story:** As an Axolync maintainer, I want new repo onboarding to include warning-proof tests, so descriptor fallback warnings are caught before merge.

#### Acceptance Criteria

1. WHEN a new consumed repo is added to Builder/report surfaces THEN the skill SHALL require tests proving the repo resolves descriptor exports.
2. WHEN a repo is expected to avoid fallback warnings THEN the skill SHALL require a report or unit test proving no descriptor fallback warning is emitted for that repo.
3. WHEN the repo checkout is missing THEN the skill SHALL distinguish managed-checkout/environment warnings from descriptor-invalid warnings.

### Requirement 4: Workspace Boundary

**User Story:** As an Axolync maintainer, I want the skill to preserve strict workspace boundaries, so agents do not mutate other agents' workspaces.

#### Acceptance Criteria

1. WHEN the skill describes repo creation or checkout THEN it SHALL require work to happen only in the current workspace.
2. WHEN another agent workspace is referenced THEN the skill SHALL allow read-only handoff inspection only if explicitly requested.
3. WHEN the skill is updated THEN it SHALL remain a workspace skill in `axolync-agent`, not a user-global `~/.codex` mutation.

