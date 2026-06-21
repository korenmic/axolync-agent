# Requirements

## Introduction

Agent version tooling must report generated artifact evidence beside primary repo version authority.

## Requirements

### Requirement 1

**User Story:** As an agent using version skills, I want artifact version drift to be visible during inventory and verify, so bumps cannot leave generated ZIP/browser metadata stale.

#### Acceptance Criteria

1. WHEN inventory runs THEN it SHALL include generated artifact evidence status.
2. WHEN verify runs THEN it SHALL fail if generated artifact evidence disagrees with version authority.
3. WHEN evidence is missing THEN it SHALL report missing evidence separately from drift.
4. WHEN plan/apply bump output is generated THEN it SHALL include enough evidence fields to know what must be regenerated.

### Requirement 2

**User Story:** As a future agent, I want skill docs to reflect the new version standard, so version bumps continue to use the single authority model.

#### Acceptance Criteria

1. `bump-version-tags` docs SHALL state that package ZIP and browser preinstalled metadata checks are part of a complete bump.
2. `version-tags-table` docs SHALL state that artifact evidence columns are consumer evidence, not authority.
