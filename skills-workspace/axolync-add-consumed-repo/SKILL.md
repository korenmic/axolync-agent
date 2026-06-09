---
name: axolync-add-consumed-repo
description: Add or review a new Axolync repository as a consumed repo across descriptors, builder wiring, reports, catalogs, seeds, addon artifacts, and applicable tests. Use when the user says add-repo, add-axolync-repo, axolync-consumed-repo, register-axolync-repo, asks to add a new Axolync repo, register a consumed repo, wire a repo into builder/report outputs, or validate repo onboarding completeness.
---

# Axolync Add Consumed Repo

Use this skill when a new repository enters the Axolync repo group or when an existing repo must become a consumed input to builder/report/artifact flows.

This is Axolync-specific workspace guidance. Do not use it as a generic GitHub repo onboarding checklist.

## Core Rule

Adding a repo is not complete when the folder exists or a descriptor exists.

A consumed repo is complete only when every applicable Axolync consumption surface is either wired or explicitly declared not applicable.

## Workspace Boundary

- Make source changes only in the current workspace's local repos.
- Treat other agents' workspaces as read-only unless the current task explicitly allows a root-level handoff file.
- Do not build, checkout, install dependencies, or write infrastructure in another agent's workspace.

## Classification First

Before editing, classify the repo. More than one may apply.

- `contract`: OpenAPI/schema/shared plugin contract authority.
- `builder`: build/report/orchestration authority.
- `browser`: browser app/runtime authority.
- `platform-wrapper`: Android/iOS/desktop wrapper authority.
- `addon`: installable or preinstallable addon package repo.
- `adapter-catalog`: adapter candidate catalog, research, seed, or adapter manifest authority for one or more controller lanes.
- `addon-pack`: repo that consumes selected addon repos/packages and exports an installable/preinstallable pack or pack-definition authority. It is both a `consumer` and a `consumable`.
- `plugin`: legacy-only first-party bridge package repo. Do not use this classification for new repo naming unless the task is explicitly about existing `*-plugin` repos.
- `theme`: installable or preinstallable theme package repo.
- `agent-tooling`: agent skills, seeds, dispatch, workflow, or automation repo.

Use the classification to decide which surfaces below apply. Do not blindly add all surfaces.

## New Repo Creation Gate

When the requested repo does not exist yet, create only the minimal repo shell needed for the current task unless the user or seed explicitly asks for bootstrap, build, package, or artifact work.

Default minimal shell may include:

- GitHub repo and local sibling clone.
- README or project seed describing purpose.
- `axolync.repo.toml` when descriptor authority applies.
- repo-local project seed placeholders when applicable.
- adapter/catalog placeholders only for controller-lane or adapter-authority repos where the current task explicitly asks for catalog/discovery scaffolding.
- minimal tests only when they prove descriptor, discovery, or catalog wiring requested by the current task.

Do not install dependencies, bootstrap the repo, run full builds, generate package ZIPs, add preinstalled defaults, or stage generated artifacts unless explicitly required by the current task.

Do not create catalog placeholders for ordinary addon, theme, wrapper, builder, contract, or agent-tooling repos unless the user or seed explicitly defines that repo as adapter catalog authority.

Classify new repos by role, not by legacy naming. Artifact packaging, preinstalled defaults, and builder build-profile changes are applicable only when the current task explicitly asks for artifact composition or when the repo already has shippable runtime contents.

## Required Surfaces

For every consumed repo:

- Add or update repo descriptors in the owning repo and consumer repo when the descriptor model applies.
- Treat repo-local `axolync.repo.toml` exports as the only accepted source for repo-owned production surfaces in newly created or newly onboarded repos.
- Declare applicable `[exports.tests]`, `[exports.packaging]`, `[[exports.generated_outputs]]`, `[[exports.inventories]]`, `[exports.docs]`, and `[[consumes.repos]]` entries in the repo descriptor before adding consumer/report wiring.
- For addon-pack repos, set descriptor roles to `["consumer", "consumable"]`, declare member addon repos under `consumes.repos` with `use = "addon-pack-member"`, and declare the final pack artifact as an export. Do not model generated member ZIPs as consumed repos.
- Update builder repo discovery only for builder-owned fields such as `id`, `localPath`, `submodulePath`, `submoduleUrl`, `versionFile`, and `cleanPaths`.
- Do not add new repo-owned fallback authority to builder `config/repos.json`. Forbidden fields for new onboarding include `buildCommands`, `sanityCommands`, `testCommands`, `addonPackage`, `themePackage`, `addonPackPackage`, `plugin`, `adapterCatalogManifestPath`, and `adapterCatalogManifestProfileId`.
- Add tests that prove the repo is discoverable from the intended consumer, not just present on disk.
- Keep builder-owned fields and repo-owned descriptor fields separated. If a field is transitional, document and test the boundary.

For repos that participate in reports:

- Add report profile inclusion where the report should inspect the repo.
- Add task/seed metadata references if the repo has project seeds or spec tasks.
- Add platform-report or inventory tests that prove the repo's rows are present and truthful.
- Add a descriptor fallback warning regression that proves the new repo emits no descriptor fallback warnings when its descriptor checkout is available.
- If a local checkout is absent, classify that as managed-checkout/environment debt, not proof that repo-owned descriptor exports are invalid.

For addon, addon-pack, legacy plugin, or adapter-catalog repos:

- Add adapter catalog inventories in `axolync.repo.toml` when the repo exposes runtime adapters.
- Add addon package ZIP metadata in descriptor packaging/generated output exports when the repo should produce an installable addon artifact.
- Add package commands and output ZIP paths in descriptor exports used by builder.
- Add installable-artifact report coverage.
- Add preinstall metadata only when the repo should ship preinstalled in an artifact profile.
- Add or update build-preset TOML preinstalled addon lists only when the product artifact should include the addon by default.
- Preserve the distinction between `installable addon artifact ZIP` and `preinstalled addon package`.
- For addon-pack repos, preserve the distinction between member addon package ZIPs and the final pack ZIP. Builder may consume member repo exports, but generated ZIP outputs are never role-bearing repos.
- For adapter-catalog repos, keep catalog/report wiring independent from package ZIP publication unless the task explicitly asks for a shippable runtime package.

For native-capable addon repos:

- Add native companion metadata only when the addon owns a native service/helper.
- Add wrapper support declarations and native payload staging validation where applicable.
- Use `addon-native-runtime-operator` as the deeper workflow when native helper implementation is required.

For wrapper/platform repos:

- Wire wrapper source authority and compatibility/migration state.
- Add artifact publication, manifest, and staging tests for the wrapper outputs that builder should produce.
- Avoid treating wrapper artifacts as generic addon artifacts.

For contract repos:

- Change contracts only when a shared API/schema shape changes.
- Add generated schema, fixture, and conformance coverage when contracts do change.
- Do not add contract churn merely because a repo is newly consumed by builder.

For agent/tooling repos:

- Add them to builder or report catalogs only when they are intended as consumable project assets.
- Keep workspace skills separate from user-global skills.
- Do not assume agent-tooling repos produce APK/EXE/addon artifacts.

## Implementation Sequence

1. Identify the requested repo, branch, and local sibling path.
2. Classify the repo type and list applicable consumption surfaces.
3. Inspect existing nearby repo entries and mirror their structure where the classification matches.
4. Update descriptors before consumer wiring when descriptor authority exists.
5. Update builder/report/catalog/artifact wiring only for applicable surfaces, keeping `config/repos.json` limited to builder-owned discovery fields.
6. Add focused tests for descriptor discovery, builder config projection, report inclusion, adapter catalog inclusion, and artifact ZIP publication as applicable.
7. Add warning-proof tests that fail if descriptor-owned surfaces fall back to legacy builder config while the descriptor checkout is present.
8. Run the narrowest relevant tests first.
9. If a full build/report is requested, hand off to the build/mirror workflow after the repo wiring tests pass.

## Review Checklist

Before calling the work complete, answer these explicitly in your final response or CR notes:

- Which repo type did you classify this as?
- Which descriptor files changed?
- Which builder/report surfaces now consume the repo?
- Does it produce installable artifacts, preinstalled artifacts, both, or neither?
- Are adapter catalog rows expected? If yes, where are they sourced?
- Are seeds/spec tasks expected? If yes, where are they indexed?
- Are contracts unchanged intentionally, or changed with schema/fixture coverage?
- Which tests prove the wiring?

## Common Failure Modes

- Adding only a local sibling repo without builder/report discovery.
- Adding repo-owned commands, package metadata, or catalog paths to `config/repos.json` instead of descriptor exports.
- Adding `config/repos.json` entries without repo descriptors or boundary tests.
- Adding an addon package ZIP but forgetting report/installable artifact coverage.
- Adding an addon to preinstalled profiles when it should only be installable.
- Forgetting adapter catalog manifest metadata for a runtime adapter repo.
- Changing contracts for repo registration when no shared API shape changed.
- Using another agent workspace for checkout/build instead of the current workspace.
