# Local Dependency Bootstrap Policy

This policy exists to stop the recurring "declared package exists in `package.json`, but local `npm run dev`/`build`/`test` still crashes after pull" class of regressions.

## Rules

1. Any third-party import added under `scripts/` or any npm lifecycle path must land with the corresponding `package.json` and `package-lock.json` update in the same change.
2. Any lifecycle entrypoint that can execute before a developer manually reruns `npm install` must start behind `scripts/ensure-local-deps.mjs`.
3. Each change that affects this boundary must add or maintain regression coverage for:
   - the bootstrap behavior itself
   - the package-script guard that keeps lifecycle entrypoints behind the bootstrap
4. A clean CI run on a fresh install is not enough proof by itself. Local entrypoints must also stay safe after ordinary `git pull` / rebase workflows with stale `node_modules`.

## Why This Exists

Fresh CI installs can hide a real local developer regression: a repo may have the right declared dependencies, but local lifecycle scripts can still crash before the next manual `npm install` if `node_modules` is stale. This policy keeps local entrypoints self-healing and reviewable.
