# 011: TDD red/green commits

Status: accepted for trial as an opt-in `init` feature (since KB-228); benefit not yet measured

## Decision

When work is test-driven, record it as two commits: the failing tests alone (`KB-NNN: test: ...`, trailer `TDD: red`, line `Expected failing: <test ids>`), then the solution (`KB-NNN: ...`, trailer `TDD: green`). Documentation, exploratory work, and configuration are exempt. The rule is the `tdd-commits` feature of `/kaboost:init` (KB-228): a block in the project's `AGENTS.md` and the audit script `scripts/kaboost_audit_tdd.py`. The core rules keep only "use TDD where suitable"; until KB-228 the commit split was a core line and a paragraph of the adaptive workflow, which asked every project for two commits per change.

`scripts/kaboost_audit_tdd.py [range] [--run 'cmd {tests}']` pairs each red with the next green of the same task and reports: a red without a green (or the reverse), a missing task ID or `Expected failing:` line, a red commit that touches non-test files, a green commit that touches only test files. With `--run` it checks out both commits in detached worktrees and requires the named tests to fail on red and pass on green.

CI: a red commit fails by design. Push-triggered runs skip a head commit whose message contains `TDD: red` (the `if` on the full-cycle job; the `ci-python` init feature carries the same condition), and pull-request runs never skip, so the pull-request head is always checked and a branch can never be merged with an unchecked red head. Pushing the pair together also works. Find the first failing commit with `git bisect --first-parent`, which stays on merge commits, and do not squash-merge a branch whose pairs should stay minable.

## Evidence

None yet for benefit. The motivation is that the pairs are minable as fail-to-pass tasks for the evaluation work ([ADR 008](008-evaluation-criteria.md), KB-216) and for process review: the split makes "tests came first" checkable from history. ADR 008 requires evaluation before adopting a rule on benefit grounds, so this is a trial: KB-025 collects about twenty pairs from real use of the release candidate, and KB-213 measures the context cost of the added text. If the pairs show no better compliance or less rework, remove the rule.

## Alternatives and tradeoffs

- **One commit with tests and fix:** simpler, but "tests first" cannot be checked and the pair cannot be mined.
- **Tests first in the PR description only:** not mechanically checkable.
- **A hook that rejects red commits locally:** red commits are legitimate, so a hook would need to know the trailer; deferred to KB-226 (agent hooks).

## Consequences

- Costs no always-loaded context; a project opts in with `/kaboost:init` (in kaBoost itself through the same feature).
- The audit script's source is `init/features/audit_tdd.py`; the feature copies it into the project as a managed file, so `init` reports and applies updates.
- A pushed red commit fails CI wherever the skip condition is missing; only the `ci-python` feature carries it, so the feature text tells projects to add it or push the pair together.
- Squash merges lose the pairs; the project's merge policy decides whether the rule is usable.
