# 005: Environment boundary

Status: accepted

## Decision

Keep toolkit autonomous; reserve machine reconciliation for a future separate project.

## Alternatives and tradeoffs

Combining dotfiles, secrets, package distribution, and engineering workflows creates unrelated lifecycle coupling.

## Consequences

No sync engine or environment repository now. Later consume toolkit releases through existing environment-management tools.
