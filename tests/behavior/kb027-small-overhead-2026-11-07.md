# KB-027 Small-task overhead on the release content — 2026-11-07

Measures the roadmap release gate "Small-task median time/token overhead at most 20%" on the content released as `v0.1.0`, which equals `v0.1.0-rc.3`: a 46-line core imported by the project, and the plugin with four skills and seven commands. The [KB-217 A/B](kb216-calibration-2026-10-30.md) ran before the KB-222 and KB-218 core additions (core 40 lines), so it does not cover this content.

## Setup

- Task `ah-queue-idle-gap` from the public aHerald repository, with the oracle and prompt of KB-217; the corrected prompt and the per-session cargo target were ported to master in `ce3b1df` (they had stayed on the calibration branch). Runner: [run_calibration.py](run_calibration.py) at that commit.
- Arms: BASE (no toolkit) and V0 (project-local core import and plugin, natural skill routing), 10 sessions each, shuffled, run one at a time.
- Windows 11 Pro 22621, Claude Code 2.1.316, `claude-sonnet-5-5`, medium effort, USD 0.40 cap per session. The runner passes `--setting-sources project,local`; anything else the client loads from the profile is the same for both arms.
- Classified as Small under the [adaptive workflow](../../workflows/adaptive.md): a focused fix in one module with a regression test, no public contract or security impact.

## Results

| Measure | BASE | V0 |
| --- | --- | --- |
| Oracle passed | 8/10 | 10/10 |
| Median total tokens per session | 155,073 | 147,185 |
| Median input tokens of the first turn | 13,184 | 14,918 |
| Median agent cost per session | USD 0.132 | USD 0.127 |
| Mean agent cost per session | USD 0.138 | USD 0.130 |
| Cost per passing session | USD 0.172 | USD 0.130 |
| Median wall time | 85.0 s | 55.6 s |
| Planning skill invoked | 0 | 0 |

Overhead of V0 against BASE: median total tokens −5.1%, median cost −4.2%, median wall time −34.6%. The gate (at most +20%) is met on this task. Per-session record: [CSV](kb027-small-overhead-2026-11-07.csv).

## Limits

- One task and 10 sessions per arm. The pass difference (8/10 against 10/10) is not significant (Fisher exact, two-sided p ≈ 0.47) and is not an improvement claim.
- Tokens were read afterwards from the session event logs of the run (not committed) into a [token CSV](kb027-small-overhead-2026-11-07-tokens.csv): total tokens are the input, cache-creation, cache-read and output tokens of the final `result` event, dominated by cache reads; cost is the client's `total_cost_usd`.
- The release content reached every V0 session: the `kaboost` plugin and its skills appear in the init event of 10/10 V0 sessions and 0/10 BASE sessions, and the first turn's input is about 1,730 tokens larger in V0, more than the skill and command listing alone (364 estimated, [context overhead](../../docs/context-overhead.md)); the core and listing together are estimated at 1253 by characters ÷ 4.
- Wall time includes cargo builds. Three BASE sessions took over 140 s, two of which failed the oracle; the time difference rests on them and is not evidence of a speed-up.
- Conditions differ from KB-217: Windows instead of macOS (the real Windows binary is built, not the shim), Claude Code 2.1.316 instead of 2.1.308. BASE passed 8/10 here against 7/10 there.
- Judge defect: for toolkit arms the candidate diff includes the files the harness adds (`.claude/engineering-rules.md`, `CLAUDE.md`), so the judge scored "minimal" 2 in every V0 session, and `files_changed` counts those two files. Judge scores for toolkit arms here and in KB-217 are biased against the toolkit (KB-234); the judge is not used for the gate.
- Cost of the run: agents USD 2.68, judge about USD 0.65.
