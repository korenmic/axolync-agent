---
name: claudify
description: Generate Claude-compatible copies of the Axolync agent skills from the canonical Codex sources, auto-install the workspace skills into the workspace .claude/skills, and offer to install user skills globally by hand. Use when invoked as $claudify or when the user asks to (re)generate Claude skills from the Codex sources.
---

# Claudify

Use this skill to regenerate Claude-form skill copies from the canonical Codex skill sources. The Codex `$name` sources stay the single source of truth; this only generates copies.

## What it does

- Runs `scripts/claudify.py`, which converts known-skill `$name` invocations into `/name` and leaves every other `$` usage and file path untouched.
- Writes all generated copies into the gitignored `.claudify-out/` directory under the agent repo.
- Auto-installs (replaces) the workspace-skill copies into the workspace `.claude/skills`.
- Generates the user-skill copies but never installs them globally.

## Run

From the agent repo root:

```
python scripts/claudify.py
```

Optional arguments:

- `--no-install`: generate only; do not touch the workspace `.claude/skills`.
- `--workspace <dir>`: override the workspace root used for the `.claude/skills` install.
- `--output <dir>`: override the output directory.

## After running

The script prints an offer to install the user skills globally, with exact source and destination paths. Always echo that offer to the user. User skills are never auto-installed; installing them is a manual step, usually done once per environment. Do not perform the global user-skill install automatically.

## Notes

- Only the generated copies use `/name`. Never write `/name` invocations into the tracked sources.
- CI proves the transform never over-reaches (reversing the output reproduces the source) and that every skill still generates, so adding a new skill cannot silently break claudify.
