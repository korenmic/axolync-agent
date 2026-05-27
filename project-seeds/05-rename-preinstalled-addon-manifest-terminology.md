# Rename Preinstalled Addon Manifest Terminology

## Summary

Rename the confusing browser preinstalled addon manifest terminology that still says `plugin` and `bridge` even though the payloads are modern Stage 1 addon ZIPs.

The current implementation is functionally correct after the hash sidecar split, but names like `public/plugins/preinstalled`, `sync-preinstalled-bridge-bundles.mjs`, and `PreinstalledPluginManifestEntry` make the code look like it belongs to deprecated pre-stage-1 plugin infrastructure. This seed exists to clean up that naming without changing runtime behavior.

## Product Context

Axolync now treats shipped preinstalled packages as Stage 1 installable addon ZIPs. The old "plugin" and "bridge bundle" language causes review/debug confusion because:

- it sounds related to deprecated pre-stage-1 plugin ZIP outputs
- it hides that these are Stage 1 addon manifests and addon package hashes
- it makes generated manifest dirt look suspicious even when it belongs to the modern preinstall flow
- it increases the chance that future cleanup deletes or avoids the wrong code path

The goal is vocabulary truthfulness: modern addon packaging should use addon names, and legacy plugin names should only remain where legacy behavior truly still exists.

## Recommended Naming Direction

Preferred canonical vocabulary:

- `preinstalled addon` for shipped Stage 1 addon ZIPs
- `preinstalled addon manifest` for stable tracked manifest metadata
- `preinstalled addon hashes` for generated content hashes
- `addon bundle sync` or `preinstalled addon sync` for the build-time script that packages and copies the ZIPs

Recommended concrete renames:

- `public/plugins/preinstalled/` -> `public/addons/preinstalled/`
- `public/plugins/preinstalled/manifest.json` -> `public/addons/preinstalled/manifest.json`
- `public/plugins/preinstalled/manifest.hashes.json` -> `public/addons/preinstalled/manifest.hashes.json`
- `scripts/sync-preinstalled-bridge-bundles.mjs` -> `scripts/sync-preinstalled-addon-bundles.mjs`
- `PREINSTALLED_PLUGIN_MANIFEST_PATH` -> `PREINSTALLED_ADDON_MANIFEST_PATH`
- `PREINSTALLED_PLUGIN_MANIFEST_HASHES_PATH` -> `PREINSTALLED_ADDON_MANIFEST_HASHES_PATH`
- `PreinstalledPluginManifestEntry` -> `PreinstalledAddonManifestEntry`
- `PreinstalledPluginManifestHashEntry` -> `PreinstalledAddonManifestHashEntry`
- `normalizePreinstalledPluginManifestEntry` -> `normalizePreinstalledAddonManifestEntry`
- `loadPreinstalledPluginManifestHashes` -> `loadPreinstalledAddonManifestHashes`
- `seedPreinstalledPluginsFromManifest` -> `seedPreinstalledAddonsFromManifest`
- bootstrap log text `Preinstalled plugin ...` -> `Preinstalled addon ...`

Acceptable fallback if public URL churn is considered too invasive:

- Keep the public URL path for one implementation pass, but rename all source symbols and scripts from `plugin`/`bridge` to `addon`.
- Add a follow-up task to rename the public path once all builder/report/artifact references are known.

## Technical Constraints

- Do not change the package format or Stage 1 addon runtime behavior.
- Do not resurrect or preserve deprecated pre-stage-1 plugin outputs.
- Keep `manifest.json` as the stable tracked metadata file.
- Keep generated content hashes split into an ignored sidecar.
- If the public URL path changes, update all browser, builder, wrapper, and tests that read or copy the preinstalled addon manifest assets.
- If backward compatibility is kept, it must be explicitly transitional and must not imply legacy plugin support.
- Do not rename broad classes like `PluginStorage` unless a separate broader storage-domain rename is intentionally scoped; this seed is about preinstalled addon manifest terminology only.

## Proposed Scope

1. Audit current misleading names.
   - Find references to `preinstalled plugin`, `plugins/preinstalled`, and `preinstalled bridge bundle`.
   - Classify each as modern Stage 1 addon preinstall terminology versus real legacy plugin terminology.

2. Rename source symbols.
   - Rename preinstalled manifest interfaces, constants, helper functions, tests, and bootstrap log names from plugin to addon where they represent Stage 1 addon packages.
   - Preserve `PluginStorage` class naming unless a broader storage rename is separately approved.

3. Rename build script.
   - Rename `sync-preinstalled-bridge-bundles.mjs` to `sync-preinstalled-addon-bundles.mjs`.
   - Update npm scripts and any builder/report references.
   - Keep script behavior equivalent.

4. Decide and implement public path rename.
   - Preferred path is `public/addons/preinstalled`.
   - If implemented, update runtime fetch URLs, tests, generated artifact layout, and report inspections.
   - If deferred, document why and leave a focused follow-up task.

5. Preserve hash-sidecar behavior.
   - Stable manifest remains tracked.
   - Hash sidecar remains generated and gitignored.
   - Parity tests still verify sidecar hashes match ZIP bytes.

6. Add regression coverage.
   - Tests should prove the runtime loads modern preinstalled addon manifests from the canonical path.
   - Tests should prove no checked-in generated hash churn returns to `manifest.json`.
   - Tests should ensure old `bridge` wording does not remain for modern preinstalled addon code paths.

## Resolved Decisions

- The current hash sidecar is modern Stage 1 addon infrastructure, not deprecated legacy plugin infrastructure.
- The misleading names should be corrected because they cause wrong mental models during reviews and cleanup.
- The best vocabulary is `addon`, not `plugin`, for these preinstalled packages.
- The best script name is `sync-preinstalled-addon-bundles.mjs`.
- `manifest.hashes.json` is acceptable as a sidecar name if it lives under a truthful addon path; otherwise `preinstalled-addon-hashes.json` is also acceptable.
- Broad storage naming is out of scope unless separately approved.

## Open Questions

1. Should the public URL move immediately from `/plugins/preinstalled/` to `/addons/preinstalled/`, or should that be a second PR after source-symbol cleanup?
2. Should the ignored hash sidecar remain named `manifest.hashes.json`, or should it become `hashes.json` under the new addon manifest directory?
3. Should runtime keep a temporary fallback from the new addon URL to the old plugin URL for one release, or should there be no compatibility path because code and assets are built together?
