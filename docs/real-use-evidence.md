# Real-use evidence (KB-025)

Criteria fixed on 2026-11-08, before any data was collected, so that the result cannot shape them. They gate nothing ([ADR 012](decisions/012-stable-release-gates.md)); the result goes into the [gate assessment](release-gate-assessment.md). The numbers describe a few repositories and one maintainer. They are not a statistical test, and a small difference is reported as no difference.

## What is measured

The question is whether the opt-in `tdd-commits` feature (`v0.2.0`) produces valid red/green pairs in ordinary work and whether rework does not grow after it is enabled.

| Repository | Role | Baseline window | Treatment window |
| --- | --- | --- | --- |
| [aHerald](https://github.com/proprock/aHerald) (Rust, Conventional Commits with the task ID at the end, merge commits) | M1 and M2 | First commit (2026-10-24) to the commit that enables `tdd-commits` | After that commit until the time box ends |
| kaBoost | M1 only: the rule has been in force since the first commits, so there is no baseline; its pairs come from agent sessions the maintainer supervised closely | None | Commits after 2026-11-08 |

Each repository listed in the boundary table below is measured like aHerald (M1 and M2, its own baseline) from its own boundary commit. Another repository joins only if `tdd-commits` is enabled in it with a recorded boundary commit and it has at least two weeks of history before that commit.

The boundary is the merge commit on `master` that brings in the `tdd-commits` block. Record its SHA and date in the table below when it lands; everything after it on the first-parent line of `master` is treatment. watchdog and the private repository develop on a local chain of feature branches rather than on `master`; there the boundary is the local commit that adds the block, and treatment is `<boundary>..<tip of the chain>`.

| Repository | Boundary commit | Date |
| --- | --- | --- |
| aHerald | `829e5c8` (merge of [aHerald#170](https://github.com/proprock/aHerald/pull/170), AH-292) | 2026-11-08 |
| [watchdog](https://github.com/proprock/watchdog) (Conventional Commits; task IDs must move to the end of the subject, `(WD-182)`, for pairs to be found) | `0d5e984` (WD-182, local branch `feature/WD-182-tdd-commits` on `feature/WD-151`) | 2026-11-08 |
| private repository (Conventional Commits; task IDs `(ASI-N)` start with this commit; only aggregate numbers are published) | local commit (ASI-1) | 2026-11-08 |

## Metrics

**M1, pair validity.** The share of red/green pairs that `kaboost_audit_tdd.py --run` accepts: the named tests fail on the red commit and pass on the green one, and the red commit changes only tests. Structural problems (a red commit without `Expected failing:`, a red without a green) count as invalid pairs. Commands:

- aHerald: `python scripts/kaboost_audit_tdd.py <boundary>..master --run 'cargo test --workspace -- {tests}'`, on Linux, because the test command runs through a POSIX shell.
- kaBoost: `py -3 scripts/kaboost_audit_tdd.py <first treatment commit>~1..master --run 'py -3 -m unittest {tests}'`.

M1 has no baseline. It shows whether the rule works as written, not whether it helps.

**M2, rework rate (aHerald).** The share of code commits that are rework.

- A code commit is a non-merge commit reachable from `master` in the window (`git log --no-merges <from>..<to>`) that changes at least one file outside `docs/`, `*.md` and `.github/`.
- It is rework when its subject starts with `fix` (`fix:`, `fix(...)`, `fix!:`) or `Revert`, and it changes at least one code file that another code commit changed within the previous 7 days.
- Compute M2 for both windows with the same procedure. A script for this comes with the mining step, on its own branch. The definition above is fixed; the script implements it and does not change it.

**M3, manual interventions.** Not measured from git, because git cannot tell whether a human corrected an agent. The maintainer records each case where an agent broke the red/green rule and had to be corrected (wrong red commit, solution in the red commit, squash that lost a pair) in the [miss log](../tests/behavior/misses.md) with the candidate `tdd-commits`. The count is reported and not compared with a baseline.

## Time box and stop rule

- Start: the aHerald boundary commit. End: when all repositories together have 20 pairs, or six weeks after the start, whichever comes first.
- Fewer than 10 pairs at the end means the result is inconclusive: record that, stop collecting, and do not extend the window.
- Mine once at the end. Looking at interim numbers is allowed but changes nothing above.

## How the result is read

- M1 at least 80% and M2 in the treatment window at most 5 percentage points above the baseline: the rule works as written and did not raise rework. Record it as evidence for recommending `tdd-commits` to test-driven repositories. This does not show that it improves outcomes.
- M1 below 80%: the rule or the audit does not fit real work. Read the invalid pairs, then fix the rule text, the audit or the CI guidance, and record that as a finding.
- M2 more than 5 percentage points above the baseline: record that the window showed more rework after enabling the rule. With samples this size it is a warning to look at the rework commits, not proof of harm.

## Results

Not collected yet.
