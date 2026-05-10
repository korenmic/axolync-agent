Implement a new addon-owned native bridge runtime operator in Axolync by following the native bridge runtime operator playbook exactly.

Canonical reference:
- `axolync-builder/docs/native-bridge-runtime-operator-playbook.md`

Reference implementation:
- `axolync-addon-vibra`
- `axolync-builder`
- `axolync-browser`
- `axolync-android-wrapper`

Use normalized terminology:
- `native bridge`
- `runtime operator`
- `native bridge operation`

Hard rules:
1. keep addon-specific logic in the addon repo
2. keep browser generic
3. keep wrapper hosts generic
4. builder owns staging and artifact proof
5. addon JS must consume a generic `getConnection()` result, not wrapper-specific fetch code
6. for Android/Capacitor, keep transport quirks Android-specific and do not regress Tauri or Electron

Required deliverables:
1. addon manifest declarations for the runtime operator and payloads
2. addon package build emitting native payload metadata
3. builder prebundled proof registration and staging
4. browser generic bridge consumption only
5. Electron host implementation if needed
6. Tauri host operator kind or descriptor support if needed
7. Capacitor plugin publication and installed-WebView invocation proof if needed
8. end-to-end tests proving the operator is staged, callable, startable, and returns a usable connection

Treat Vibra as the pattern, not as something to special-case or copy blindly.
