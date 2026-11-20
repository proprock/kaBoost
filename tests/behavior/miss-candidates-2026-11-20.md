# Miss-log candidates — 2026-11-20

Output of `scripts/kaboost_miss_candidates.py` (KB-250) on the local clones, not fetched. Candidates only: nothing here is confirmed, and no row was copied into the [miss log](misses.md); KB-254 reviews them.

## aHerald `829e5c8..master` (`master` at `a61b9c2`)

| Date | Repository | Task | What went wrong | How it was found | Candidate |
| --- | --- | --- | --- | --- | --- |
| 2026-11-10 | aHerald | AH-297 | squash merge `c76c5093a` "feat(setup): status line choice, dependencies between choices and a Done button (AH-297) (#178)" may have lost a red/green pair | git history | tdd-commits |
| 2026-11-10 | aHerald | AH-297 | `c76c5093a` "feat(setup): status line choice, dependencies between choices and a Done button (AH-297) (#178)" changes code without a `TDD: red` commit for its task | git history | tdd-commits |
| 2026-11-16 | aHerald | AH-221 | `b69391a40` "fix(test): measure the memory-growth check on its own process (AH-221)" changes code without a `TDD: red` commit for its task | git history | tdd-commits |
| 2026-11-13 | aHerald | AH-300 | `eb053fa9b` "fix(usage): prefer Claude statusLine quota in auto mode (AH-300)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |
| 2026-11-13 | aHerald | AH-300 | `306e13267` "fix(usage): bound auto quota freshness by the refresh interval (AH-300)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |
| 2026-11-16 | aHerald | AH-221 | `b69391a40` "fix(test): measure the memory-growth check on its own process (AH-221)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |
| 2026-11-16 | aHerald | AH-306 | `389a66d3f` "fix(linux): a transient card that cannot be drawn ends with the error (AH-306)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |

squash: 1
unpaired: 2
rework: 4

## watchdog `0d5e984..HEAD` (branch `feature/wd-200-compare` at `0a6cc4a`)

| Date | Repository | Task | What went wrong | How it was found | Candidate |
| --- | --- | --- | --- | --- | --- |
| 2026-11-11 | watchdog | WD-208 | `8f26a0913` "fix(registry): keep every configuration section on mutation (WD-208)" changes code without a `TDD: red` commit for its task | git history | tdd-commits |
| 2026-11-12 | watchdog | WD-184 | `82066d84a` "feat(insights): import watchdog-insights as a workspace package (WD-184)" changes code without a `TDD: red` commit for its task | git history | tdd-commits |
| 2026-11-11 | watchdog | WD-210 | `58c95dd4d` "fix(daemon): report health across all projects (WD-210)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |
| 2026-11-11 | watchdog | WD-210 | `ca2be482e` "fix(daemon): continue active transcript and maintenance work (WD-210)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |
| 2026-11-12 | watchdog | WD-214 | `74a0b658b` "fix(native): preserve events through brief admission contention (WD-214)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |
| 2026-11-12 | watchdog | WD-187 | `cac14348a` "fix: keep raw capture moving through retries (WD-187)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |
| 2026-11-12 | watchdog | WD-211 | `49bc93971` "fix(native): account for admission lock failures (WD-211)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |
| 2026-11-12 | watchdog | WD-212 | `b97ddd099` "fix: replace Windows daemon control during shared reads (WD-212)" fixes code another commit changed in the previous 7 days | git history | code review (KB-205) |

squash: 0
unpaired: 2
rework: 6
