# KB-207 harder holdout (skill rename) — 2026-10-29

Follow-up to the [first holdout](kb207-holdout-2026-10-29.md), which had an outcome ceiling. Task: "Rename the
verification skill to verify-completion. Keep everything else unchanged. Run focused checks." on the frozen pilot
commit `b1d3f01`. Dependents are discoverable by a repository search (skill directory, manifest, three test
references, one README example), and the committed generated package must be rebuilt: `build.py` refuses to delete
the stale generated directory, so the agent has to remove it itself. The [independent evaluator](acceptance_rename_skill.py)
checks the rename, unchanged skill text, manifest, rebuilt and consistent generated package, validation and packaging
tests, and absence of the old name in live files. It passed a reference solution (6/6) and failed the unmodified source.

Thirty uninstrumented Claude Code 2.1.308 / `claude-sonnet-5-5` medium-effort sessions ([per-session record](kb207-holdout-rename-2026-10-29.csv)),
ten per arm, shuffled order, four workers, USD 2.42 total (plus 0.54 in smoke and baseline probe sessions). Arms: **BASE**
(no toolkit), **V0** (the adopted ADR 006 toolkit), **V2G** (V0 with a stricter `plan-before-edit` step that requires a
written plan with fixed headings before the first edit). The reused profile and unequal permission denials limit comparison.

| Measure (10 sessions each) | BASE | V0 | V2G |
| --- | --- | --- | --- |
| Independent acceptance passed | 8 | 8 | 7 |
| Planning skill invoked | 0 | 2 | 0 |
| Written plan (criteria, non-goals, alternative) before first edit | 0 | 0 | 0 |
| Searched for the old name before the first edit | 10 | 10 | 10 |
| Agent ran packaging tests | 10 | 10 | 10 |
| Mean cost / wall time | USD 0.070 / 23.3 s | USD 0.087 / 26.2 s | USD 0.085 / 25.3 s |
| Permission denials (total) | 1 | 4 | 4 |

Observations:
- **The model finds dependents by itself here.** Every session searched for the old name first and ran the tests, so a
  prompt to discover dependents added nothing measurable. Baseline passed 8/10 and the toolkit arms did not do better.
- **Routing did not trigger.** Core names `plan-before-edit` for behavior, CLI or API changes; a rename was treated as
  routine in 8 of 10 V0 sessions. The stricter wording in V2G was never read because the skill was never invoked, so this
  does not test the visible-gate idea.
- **Failures cluster in generated-package handling.** Five of the six failing sessions left the old generated skill
  directory or old references in place (the same three checks fail together). Two of the three toolkit-arm failures with
  denials suggest a permission confounder; counts are too small to separate that from model variation.
- **Cost.** The toolkit arms cost about 24% more per session without a measured outcome gain.

Conclusion limited to this scenario: no outcome benefit and no discrimination between arms (8/10 vs 8/10 vs 7/10 at n=10).
A visible-gate measure still needs a scenario that reliably triggers the skill. KB-207 remains open.
