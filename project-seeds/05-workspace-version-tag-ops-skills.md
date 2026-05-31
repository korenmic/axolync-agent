# Workspace Version / Tag Ops Skills

## Summary

Create reusable Axolync agent infrastructure and skills for workspace-wide version/tag operations across all repos known to the current builder registry.

The workflow should cover two common needs:

- Regenerate a CLI-aligned text table of every registered repo's branch, HEAD, current version, latest/exact tag, and version/tag delta.
- Bump selected repos or all registered repos in one controlled operation, using the same version/tag infrastructure instead of ad-hoc throwaway scripts.

## Product Context

Axolync releases span many small repos. Today, a coordinated release bump requires manually pulling all repos, checking which master HEADs are already tagged, editing version files, committing, tagging, pushing, and then reporting a table. This is repetitive and easy to get wrong.

The desired end state is that Sinq agents can perform release/version hygiene with a named skill and a stable script, while preserving existing workspace boundaries and builder-declared repo authority.

## Technical Constraints

- Implement in `axolync-agent`.
- Repo discovery must use the current workspace builder registry, matching `masterify-all` / `pull-all-repos` behavior:
  - `axolync-builder/config/repos.json`
  - plus `axolync-builder` itself
  - no arbitrary sibling repo scanning
- Add a tracked script, likely `scripts/workspace_version_ops.py`.
- Add two skills:
  - a workspace/version table skill, for example `$version-tags-table`
  - a workspace/version bump skill, for example `$bump-version-tags`
- The table skill must write an output `.txt` or `.md` file under the workspace root, outside any individual repo by default.
- The table output should use CLI-shaped spacing suitable for terminal reading and dispatch handoffs.
- The bump skill must support:
  - dry-run/plan mode
  - all registered repos
  - explicit repo allowlist
  - skip already-tagged HEADs
  - verify mode after push
- Version bumps should be minor bumps by default.
- Prerelease suffixes should be dropped when promoting to a stable minor version, e.g. `2.0.0-beta.1 -> 2.1.0`.
- Package-lock roots should be kept in sync when package versions change.
- Known non-root version files should be handled intentionally:
  - `tools/package.json`
  - `plugin-client-ts/package.json`
  - `client-plugin/package.json`
  - matching Python `pyproject.toml` when it shares the same old version
  - Android Gradle `versionName` / `versionCode` where platform wrapper owns app versioning
- Repos without a tracked version file may be tag-only, but the behavior must be explicit in the plan output.
- Tags should be annotated by default.
- Pushes must be explicit and should push both commit and tag.
- The workflow must stop or require explicit override for dirty repos unless the dirty state is known generated output and safely ignorable.
- RTK command discipline must be documented for use inside the Sinq workspace.

## Proposed Scope

1. Add `workspace_version_ops.py`.
   - Share repo discovery logic with existing workspace repo ops where possible.
   - Provide subcommands such as `inventory`, `plan-bump`, `apply-bump`, and `verify`.
   - Emit both JSON and text table output.

2. Add version/tag inventory table support.
   - Include repo id, path, branch, HEAD, exact tag at HEAD, latest semver tag, current version, proposed next version, and status.
   - Write a stable output file under the workspace root, for example `VERSION_TAGS_<date>.txt`.
   - Keep the output untracked by default unless the user explicitly asks to commit it.

3. Add controlled bump planning.
   - Identify repos whose current HEAD is not exactly tagged.
   - Compute next minor version from the version file when available.
   - Fall back to latest semver tag for tag-only repos.
   - Detect tag collisions and either advance again or stop with a clear diagnostic.

4. Add controlled bump application.
   - Edit version files and lockfiles where applicable.
   - Commit each repo independently with a standard message such as `chore: bump version to <version>`.
   - Create annotated tag `v<version>`.
   - Push `master` and the tag.
   - Record a final summary table.

5. Add `$version-tags-table` skill.
   - Thin wrapper around the inventory/table command.
   - Use when the user asks to list, regenerate, save, view, or inspect all repo tags/versions.
   - Must not mutate repos.

6. Add `$bump-version-tags` skill.
   - Thin wrapper around the plan/apply/verify command.
   - Use when the user asks to bump versions/tags for selected repos or all repos.
   - Must start with a dry-run plan unless the user explicitly asks to apply immediately.
   - Must notify on completion when the user asks for notify.

7. Add tests.
   - Unit-test semver parsing and prerelease promotion.
   - Unit-test version file updates for package, package-lock, pyproject, and Gradle.
   - Unit-test tag-only repo planning.
   - Unit-test dirty repo blocking.
   - Unit-test text table formatting.

## Resolved Decisions

- This belongs in `axolync-agent`, not builder, because it is an agent/workspace orchestration workflow similar to `masterify-all` and `pull-all-repos`.
- The script should be reusable by skills and direct CLI usage.
- The generated release table should live in the workspace root and remain untracked by default.
- The default bump is minor, not patch.
- Existing exact HEAD tags mean no bump.
- Repos without version files are allowed only as explicit tag-only rows.

## Open Questions

- Final skill names: `$version-tags-table` / `$bump-version-tags` are proposed names, but may be renamed before implementation.
- Whether table output should default to `.txt` only, or support both `.txt` and `.md`.
- Whether the bump skill should create tags by default or require a `--push-tags` confirmation flag when run outside a direct user command.
