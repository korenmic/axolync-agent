# Design

## Overview

This spec updates the `nightly-ci-safe` skill text and validation tests so agent behavior matches Builder's corrected full-CI public contract.

## Current State

The skill currently references `npm run full-ci:inventory` as preflight proof. That command is being removed as public vocabulary. The skill must instead use `npm run full-ci -- --dry-run` for candidate listing and must clearly state that dry-run output is not executed proof.

## Skill Changes

The skill will describe this sequence:

1. finish queued work;
2. optionally run `npm run full-ci -- --dry-run` as cheap candidate-list preflight;
3. run `npm run full-ci` once for actual broad validation;
4. inspect Builder proof/reconciliation fields;
5. use `npm run full-ci:remaining` after fixes to plan or execute strict remaining work;
6. report invalid proof if evidence is substituted or unreconciled.

## Testing

Static skill tests should assert:

- `full-ci:inventory` does not appear;
- `full-ci -- --dry-run` appears as candidate listing;
- `npm run full-ci` appears as the full validation command;
- `full-ci:remaining` appears for continuation;
- invalid proof language remains present.

## Non-Goals

- Do not run the full CI suite.
- Do not alter Builder code in this agent seed.

