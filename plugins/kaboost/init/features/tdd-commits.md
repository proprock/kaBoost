## TDD red/green commits

- When work is test-driven, commit the failing tests alone first: message `<task ID>: test: ...`, a line `Expected failing: <test ids>` and the trailer `TDD: red`. Then commit the solution with the same task ID and the trailer `TDD: green`. Documentation, exploratory work and configuration are exempt.
- A red commit fails CI by design: skip push-triggered runs whose head commit message contains `TDD: red` and keep pull-request runs unconditional, or push the pair together.
- Merge with merge commits, not squash, so the pairs stay in history; find the first failing commit with `git bisect --first-parent`.
- Check the pairs with `python scripts/kaboost_audit_tdd.py <range> --run '<test command with {tests}>'`: the named tests must fail on red and pass on green.
