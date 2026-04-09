---
name: spec-maker
description: Generate a Kiro-for-Codex-style spec-creation prompt file from a standard project seed by cloning the observed prompt wrapper and injecting the seed's Summary, Product Context, Technical Constraints, and Open Questions sections. Use when the user wants to skip the manual Kiro wizard for seed-to-prompt generation, compare generated prompt files against the wizard output, or prototype seed-to-spec prompt automation.
---

# Spec Maker

## Overview

Use this skill when a user wants the local equivalent of the manual seed-to-Kiro prompt step:

1. take a standard project seed
2. wrap it in the observed Kiro spec-agent prompt shape
3. emit a prompt markdown file without executing that prompt

This skill is intentionally narrow:

- it generates the prompt file only
- it does not automatically run the prompt against the current chat
- it assumes the seed already exists and follows the normal four-section structure

## What It Generates

The generated prompt mirrors the observed local Kiro wizard output shape:

- fixed spec-agent system wrapper
- fixed `User Request: Create a requirements document for a new feature`
- injected seed sections under:
  - `Feature Description: Summary:`
  - `Product Context:`
  - `Technical Constraints:`
  - `Open Questions:`
- fixed footer with workspace/spec-base instructions

## Source Of Truth

This skill does not guess the wrapper text.

Instead, it clones the wrapper shape from an existing real prompt file under the workspace:

- `.codex/tmp/chat/prompt-*.md`

By default it uses the newest such prompt as the template source.

That keeps the generator aligned with the local observed Kiro output. If Kiro changes its wrapper later, regenerate using a newer real prompt file or pass `--template`.

## Seed Expectations

The seed should contain these top-level sections:

- title line starting with `# `
- `## Product Context`
- `## Technical Constraints`
- `## Open Questions`

Everything before `## Product Context` is treated as the Summary block.
Everything from `## Open Questions` to end-of-file is treated as the Open Questions block, which matches the observed prompt behavior where acceptance direction stays in that trailing block.

## Use The Generator

Run:

```powershell
python C:\Users\koren\.codex\skills\spec-maker\scripts\generate_seed_prompt.py --seed <seed-path> --workspace <workspace-root>
```

Optional arguments:

- `--output <path>`
- `--template <existing-prompt-path>`

Example:

```powershell
python C:\Users\koren\.codex\skills\spec-maker\scripts\generate_seed_prompt.py `
  --seed C:\Users\koren\src\Sinq\axolync-plugins-contract\docs\project-seeds\03-addon-owned-rich-addon-global-runtime-surfaces.md `
  --workspace C:\Users\koren\src\Sinq `
  --output C:\Users\koren\src\Sinq\.codex\tmp\chat\prompt-contract-03-spec-maker.md
```

## Output Rules

- do not execute the generated prompt automatically
- report the output file path back to the user
- when comparing against Kiro output, compare content, not filename
- preserve the observed newline style from the chosen template prompt

