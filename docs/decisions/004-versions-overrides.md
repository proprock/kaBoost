# 004: Versions and local configuration

Status: accepted

## Decision

Pin reviewed releases, update explicitly, and keep overrides outside package caches. Import core separately with authorization.

## Alternatives and tradeoffs

Automatic merges into user files risk data loss. Symlink-only deployment limits Windows. Mutable branches undermine reproducibility.

## Consequences

No installer is needed. Rollback uses native uninstall/reinstall; the separately maintained project-local core copy must also be reviewed and restored to the matching version.
