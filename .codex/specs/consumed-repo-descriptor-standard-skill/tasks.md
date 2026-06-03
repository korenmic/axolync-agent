# Consumed Repo Descriptor Standard Skill Tasks

- [ ] 1. Update the add-consumed-repo skill to require descriptor-owned exports.
  - Edit `skills-workspace/axolync-add-consumed-repo/SKILL.md`.
  - Add required descriptor export guidance for tests, packaging, generated outputs, inventories, docs, and consumed repos.
  - Make descriptor exports the default for all future applicable repos.

- [ ] 2. Remove new-repo legacy fallback guidance.
  - Explicitly reject adding new repo-owned authority to `config/repos.json`.
  - Name forbidden fields: `buildCommands`, `sanityCommands`, `testCommands`, `addonPackage`, `adapterCatalogManifestPath`, and `adapterCatalogManifestProfileId`.
  - Preserve only builder-owned discovery fields as acceptable builder config.

- [ ] 3. Add warning-proof onboarding checklist.
  - Require builder/report tests that prove descriptor exports resolve.
  - Require checks proving no descriptor fallback warnings are emitted for the new repo when the descriptor is available.
  - Distinguish missing checkout/environment warnings from descriptor-invalid warnings.

- [ ] 4. Validate and push the agent branch.
  - Review the skill text for the new descriptor-only standard.
  - Confirm workspace boundary guidance remains intact.
  - Commit and push the branch.

