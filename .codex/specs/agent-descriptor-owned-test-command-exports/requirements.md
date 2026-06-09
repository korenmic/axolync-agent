# Agent Descriptor-Owned Test Command Exports Requirements

## Requirement 1

**User Story:** As Builder, I want Agent build/test command metadata from the Agent descriptor, so reports do not rely on fallback command fields.

### Acceptance Criteria

1. WHEN Builder resolves `axolync-agent` commands THEN it SHALL use descriptor-owned build, sanity, and full-test command exports.
2. WHEN descriptor exports are available THEN Agent fallback warnings SHALL disappear.
3. WHEN the add-consumed-repo skill is updated THEN the Agent repo SHALL model the same descriptor standard.

## Requirement 2

**User Story:** As a skill maintainer, I want Agent descriptor cleanup to preserve workspace boundaries, so metadata work does not alter dispatch or skill behavior.

### Acceptance Criteria

1. WHEN this spec is implemented THEN workspace boundary guidance SHALL remain intact.
2. WHEN validation runs THEN command exports SHALL be discoverable without runtime behavior changes.
