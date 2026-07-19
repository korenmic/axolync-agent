# Design - Claudify Cross-Agent Skills

Derived from `requirements.md` in this spec folder.

## Components

### `scripts/claudify.py`

Single-file, standard-library-only Python script.

Core functions:

- `known_skill_names(agent_root)` -> set of skill names, taken from the immediate subdirectory names of `skills-workspace/` and `skills-user/`.
- `invocation_pattern(names, prefix)` -> compiled regex matching `prefix + name` for a known skill, with a leading boundary that excludes path characters and a trailing boundary `(?![A-Za-z0-9-])`. Names are alternated longest-first so `queue-status` wins over `queue`.
- `transform_text(text, names)` -> replace `$name` invocations with `/name` (forward).
- `reverse_text(text, names)` -> replace `/name` invocations with `$name` (used by tests to prove no over-reach).
- `claudify_bucket(src_dir, out_dir, names)` -> copy the bucket tree; transform text in `.md`, `.yaml`, `.yml`; copy every other file verbatim.
- `install_workspace_skills(out_ws_dir, dest_skills_dir)` -> replace `dest_skills_dir` contents with the generated workspace copies.
- `main()` -> orchestrate.

Boundary rationale: the leading lookbehind `(?<![A-Za-z0-9._/-])` before the prefix means a `/name` inside a path such as `skills-user/queue-status` is not treated as an invocation, while a backtick- or space-preceded `/queue-status` is. The same matcher is used for both directions, so reverse(forward(source)) == source holds for correctly-scoped input.

Only `.md`, `.yaml`, `.yml` files are transformed. Scripts (`.py`, `.ps1`, `.sh`) are copied verbatim, which also removes any chance of touching PowerShell `$var` tokens.

### CLI

```
python scripts/claudify.py [--agent-root DIR] [--workspace DIR] [--output DIR] [--no-install]
```

Defaults:
- `--agent-root`: the repository root containing `scripts/claudify.py`.
- `--workspace`: the parent of the agent root (the multi-repo workspace root).
- `--output`: `<agent-root>/.claudify-out`.
- Workspace install destination: `<workspace>/.claude/skills`.

### Output layout

```
<agent-root>/.claudify-out/
  skills-workspace/<skill>/...
  skills-user/<skill>/...
```

### Install behavior

- Workspace: `<workspace>/.claude/skills/<skill>` is replaced from `.claudify-out/skills-workspace/` on each run (unless `--no-install`).
- User: never auto-installed. The script prints an offer with the exact `.claudify-out/skills-user` source and `~/.claude/skills` destination.

## Tests (`tests/test_claudify.py`)

- `test_no_over_reach`: run claudify into a temp output; for every generated file, assert `reverse_text(output) == source`. This proves only known-skill invocations changed.
- `test_known_skill_invocations_converted`: assert at least one real invocation (e.g. `$queue-status`) became `/queue-status` in the generated copy, so the transform is actually active.
- `test_non_skill_dollar_preserved`: assert PowerShell/other `$` tokens (e.g. `$true`, `$env:`) in copied content are unchanged.
- `test_coverage_all_skills_generated`: every source skill dir in both buckets has a matching generated output dir.
- `test_source_guardrail_no_slash_invocations`: no tracked source file contains a `/name` invocation for a known skill.

## GitHub Actions (`.github/workflows/claudify.yml`)

- Trigger: push and pull_request.
- Steps: checkout, set up Python, run `python -m unittest tests.test_claudify -v`.

## Rogue invocation escaping (R7)

- `escape_rogue_invocations(text, names)` inserts a space into any invocation-position `/name` for a known skill (`/name` -> `/ name`), using the same path-safe `SLASH_CANDIDATE_RE`, so file paths are untouched.
- `transform_text` runs escaping first (on the original source, which has no legit `/name`), then converts `$name` -> `/name`. Order matters: escaping the source first means the real invocations created from `$name` are never escaped.
- `reverse_text` undoes both steps (`/name` -> `$name`, then `/ name` -> `/name`) so the no-over-reach test still holds.
- Rationale for zero-provenance-needed: because Codex sources never use `/name` intentionally, every pre-existing `/name` is safe to escape; no need to distinguish innocent-vs-intended.

## Uninventoried allowlist (R8)

- `UNINVENTORIED_ALLOWLIST` is a per-file map of expected uninventoried `$`-candidates (currently `{"skills-workspace/claudify/SKILL.md": {"name"}}`).
- `test_per_file_uninventoried_allowlist` fails if any file contains an uninventoried `$`-candidate not allowed for that file, surfacing typos/unexpected candidates for review.

## Additional tests

- `test_rogue_slash_invocation_is_escaped_and_reversible`: `/tactic` prose becomes `/ tactic`, `$tactic` becomes `/tactic`, and reverse restores the original.
- `test_paths_are_not_escaped`: a path like `skills-user/tactic/SKILL.md` passes through unchanged.

## Gitignore

Add `.claudify-out/` to `.gitignore`.
