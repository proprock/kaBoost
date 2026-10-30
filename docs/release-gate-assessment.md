# Release gate assessment

Assessed 2026-10-30 against the gates in the [roadmap](roadmap.md) for the release candidate `v0.1.0-rc.2`. Unmeasured items are labeled unassessed, not passed. The behavior work is a pilot plus later experiments, not statistical proof.

| Gate | Status | Evidence and limits |
| --- | --- | --- |
| No critical requirement, security, or boundary violation | Met for the pilot tasks; not assessed beyond them | The three pilot reports ([first](../tests/behavior/pilot-results-2026-10-29.md), [retest](../tests/behavior/pilot-retest-results-2026-10-29.md), [follow-up](../tests/behavior/pilot-followup-results-2026-10-29.md)) record none identified in manual review. Later experiments did not review diffs for such violations; the blind diff judge was not reliable enough to use ([calibration](../tests/behavior/kb216-calibration-2026-10-30.md)). |
| Quality no worse than baseline | Met within the limits of small samples | Independent acceptance: skill-routing arm equal to baseline on every task with a usable comparison (holdout 10/10 against 10/10; rename 8/10 against 8/10; idle-gap 7/10 against 7/10; Large 0/30 in all arms, a floor effect). `/kaboost:plan` passed 10/10 against 7/10 on idle-gap, not significant (p = 0.21). No arm did worse. |
| Small-task median time and token overhead at most 20% | Time met; tokens unassessed | Small median wall time was 13.3% lower, 0.2% lower, and 26.7% lower than baseline in the three pilots. Small-task token or cost overhead was not measured against a no-toolkit arm. |
| Improvement over baseline | Not demonstrated | This is not a release gate, but no experiment showed better task outcomes. The written plan from `/kaboost:plan` is produced reliably on Large tasks (10/10, against 0/10 without it) and costs about 74% more per session on the one calibrated small task. Six of seven calibrated real tasks were at the baseline ceiling. |
| Release inventory, changelog, source SHA, license, secret scan, native loading | Met for `v0.1.0-rc.2` | See [compatibility](compatibility.md) and the completed review (KB-019). Loading verified for Claude Code 2.1.312 (Linux, local) and Codex CLI 0.165.0 with profile caveats. |
| Remote install and tag pinning | Partly met | Clean-profile install and update/rollback verified on macOS, Claude Code 2.1.308 (KB-021). Linux and Windows are untested. |

## Conclusion

The candidate meets the stated non-inferiority gates where they were measured, with the gaps above labeled. It does not demonstrate better outcomes. The stable `v0.1.0` waits for evidence from real use of the candidate (KB-025) rather than for more laboratory scenarios.
