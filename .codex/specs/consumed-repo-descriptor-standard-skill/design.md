# Consumed Repo Descriptor Standard Skill Design

## Overview

Update the repo-tracked `axolync-add-consumed-repo` workspace skill so its default onboarding model matches the CI-group descriptor standard. The skill should stop presenting legacy `config/repos.json` command/package/inventory fields as acceptable for new repos.

This is agent guidance work only. It does not directly modernize every existing repo.

## Skill Text Changes

Revise the skill in `skills-workspace/axolync-add-consumed-repo/SKILL.md`.

The revised guidance should:

- define descriptor-owned surfaces clearly,
- instruct agents to add `axolync.repo.toml` exports before builder/report wiring,
- list forbidden legacy fallback fields for new repos,
- separate builder-owned discovery fields from repo-owned exports,
- require tests proving descriptor export resolution and absence of fallback warnings.

## Descriptor-Owned Export Checklist

The skill should include a checklist for applicable descriptor sections:

- `[exports.tests]` for build/smoke/full test commands,
- `[exports.packaging]` for package commands and package outputs,
- `[[exports.generated_outputs]]` for generated artifact paths,
- `[[exports.inventories]]` for adapter/catalog inventories,
- `[exports.docs]` for README/project seed exports,
- `[[consumes.repos]]` for managed consumed dependencies,
- addon-pack member declarations when a repo is both consumer and consumable.

## Builder-Owned Boundary

The skill may still allow Builder to know:

- repo id,
- local sibling path,
- submodule path,
- remote URL,
- version file or version authority,
- clean paths/bootstrap hints when genuinely builder-owned.

It must state that these are not substitutes for repo-owned descriptor exports.

## Warning-Proof Tests

The skill should require agents to add focused tests where a new consumed repo is wired into Builder:

- descriptor exports are found,
- package/test/inventory surfaces do not fall back to legacy config,
- missing checkout is classified separately from invalid descriptor,
- report warning rows are absent for the new repo when descriptor is available.

## Compatibility Position

No backwards-compatible new-repo path is provided. Existing legacy repos may still need migration, but future repos should use the modern descriptor-owned format only.

## Validation

Because this is skill text, validation should be lightweight:

- inspect the updated skill text,
- ensure forbidden fallback fields are called out,
- ensure descriptor-owned sections are named,
- ensure workspace boundary guidance remains intact.

