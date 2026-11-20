# KB-251 Haiku calibration (partial) — 2026-11-20

Baseline-only calibration of the six public [KB-216 tasks](kb216-calibration-2026-10-30.md) on `claude-haiku-5-5`, as planned in the [behavior README](README.md#calibration-on-a-cheaper-model) and approved by the maintainer on 2026-11-20 (30 sessions, ceiling USD 16.50). Same method as KB-216 under [ADR 008](../../docs/decisions/008-evaluation-criteria.md): no toolkit, start state is the parent of the fix commit with history removed, the fix commit's own tests are the oracle. Claude Code 2.1.325 on Windows 11, USD 0.40 cap per session, per-session cargo target directory, one worker. Runner: [run_calibration.py](run_calibration.py) at kaBoost `b12496e` (unchanged since `edc81d33`); task specs: [tasks/aherald.json](tasks/aherald.json). Per-session record: [CSV](kb251-haiku-calibration-2026-11-20.csv).

**The run is incomplete: 16 of 30 sessions.** A disk guard stopped it when drive C: fell below 2 GB free during session 17. Each session copies the warmed 2.9 GB cargo target and builds into it (5.3 GB at the stop), and Windows NTFS has no copy-on-write clone like the macOS `cp -c` that KB-216 used. The runner writes `summary.csv` only at the end, so the CSV was rebuilt from the runner's per-session log lines and each session's `events.jsonl`. The private task was not run.

## Results (no toolkit)

| Task | Oracle passed | Judge overall (1–5) |
| --- | --- | --- |
| `ah-ipc-unknown-field` | 3/3 | 4, 5, 5 |
| `ah-activation-window-first` | 2/2 | 5, 4 |
| `ah-tray-mode-label` | 3/3 | 5, 4, 4 |
| `ah-queue-wait-card` | 3/3 | 3, 4, 3 |
| `ah-queue-idle-gap` | 2/2 | 4, 4 |
| `ah-usage-days-hours` | 1/3 | 4, 4, 4 |

All 16 sessions exited 0 and ran on `claude-haiku-5-5` (checked in the events). Mean agent cost USD 0.016 per session (USD 0.26 in total, judge calls not included), mean wall time 105 s, mean 17.8 turns. On Sonnet the KB-216 baseline averaged USD 0.125 per session on `ah-queue-idle-gap`.

## Reading

- With two or three sessions per task none of these rates is a calibrated value; ADR 008 asks for five.
- Five tasks passed every session, as on Sonnet, so the cheaper model alone does not take them off the ceiling.
- `ah-usage-days-hours` is the only task inside the 20–80% band so far (1/3; 5/5 on Sonnet). The judge scored the two failing sessions 4, the same as the passing one, so the judge did not see what the oracle caught; the cause of the failures is not analysed here.
- `ah-queue-idle-gap`, the only Sonnet task in the band (4/5), passed 2/2 on Haiku.

## Open

- The maintainer decides whether to complete the run (14 sessions, about 10 GB of free disk during a session) or only the two missing `ah-usage-days-hours` sessions, and which tasks enter an A/B under [ADR 013](../../docs/decisions/013-cost-per-pass-and-miss-log.md).
- The runner could write each row as it finishes and share one target with `cargo clean -p` for the workspace packages instead of a copy per session; neither is done.
