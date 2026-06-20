# Design

## Overview

This is an agent documentation and static-test change. Builder owns the command implementations; `axolync-agent` owns the wording used by skills, dispatch handoffs, and agent-facing guidance.

## Command Vocabulary

- `full-ci`: maximal descriptor-aware validation across the Builder-managed repository inventory.
- `full-ci-core`: reduced/core-only validation for intentionally scoped checks.
- `full-ci -- --dry-run`: candidate inventory/preflight only, not executed proof.
- `full-ci:remaining`: continuation targeting after an existing CI payload, not a substitute for the initial maximal proof.

## Touch Points

- `$nightly-ci-safe` skill guidance.
- Build/mirror handoff guidance where `full-ci` requests are interpreted for Sinq1.
- Static tests that guard against command-name drift.

## Non-Goals

- No Builder code changes.
- No Sinq dispatch.
- No artifact rebuilds, report regeneration, or local full-CI runs.
