# 011: TDD red/green commits

Status: accepted for trial; benefit not yet measured

## Decision

When work is test-driven, record it as two commits: the failing tests alone (`KB-NNN: test: ...`, trailer `TDD: red`, line `Expected failing: <test ids>`), then the solution (`KB-NNN: ...`, trailer `TDD: green`). The rule is one line in the core rules and a paragraph in the adaptive workflow; documentation, exploratory work, and configuration are exempt.

`scripts/audit_tdd.py [range] [--run 'cmd {tests}']` pairs each red with the next green of the same task and reports: a red without a green (or the reverse), a missing task ID or `Expected failing:` line, a red commit that touches non-test files, a green commit that touches only test files. With `--run` it checks out both commits in detached worktrees and requires the named tests to fail on red and pass on green.

CI: a red commit fails by design. CI judges the pull-request head, so push the pair together; a red commit pushed alone to a branch with push-triggered CI fails that run and that is expected. Find the first failing commit with `git bisect --first-parent`, which stays on merge commits, and do not squash-merge a branch whose pairs should stay minable.

## Evidence

None yet for benefit. The motivation is that the pairs are minable as fail-to-pass tasks for the evaluation work ([ADR 008](008-evaluation-criteria.md), KB-216) and for process review: the split makes "tests came first" checkable from history. ADR 008 requires evaluation before adopting a rule on benefit grounds, so this is a trial: KB-025 collects about twenty pairs from real use of the release candidate, and KB-213 measures the context cost of the added text. If the pairs show no better compliance or less rework, remove the rule.

## Alternatives and tradeoffs

- **One commit with tests and fix:** simpler, but "tests first" cannot be checked and the pair cannot be mined.
- **Tests first in the PR description only:** not mechanically checkable.
- **A hook that rejects red commits locally:** red commits are legitimate, so a hook would need to know the trailer; deferred to KB-226 (agent hooks).

## Consequences

- Adds one line to the core rules; the file stays at 46 lines because the line extends an existing one.
- `scripts/audit_tdd.py` lives in this repository and is not shipped in the plugin; use it from a checkout with `--repo <project>`. Shipping it with `init` is open.
- Squash merges lose the pairs; the project's merge policy decides whether the rule is usable.
