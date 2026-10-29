# Second behavior pilot retest — 2026-10-29

All 18 sessions in the [follow-up plan](pilot-followup-plan.md) completed using
the specified source, model, and isolated clones. The revised toolkit was
loaded only in toolkit arms; harness files and source HEADs stayed unchanged.
[Per-arm measurements](pilot-followup-results-2026-10-29.csv) include usage,
time, denials, and local evidence paths. Raw events and trial checkouts are in
`/tmp/kaboost-pilot-followup-20261029` and are not durable. Reported model cost
was USD 1.4736; no human intervened during a session.

| Scenario | Baseline | Revised toolkit | Review |
| --- | --- | --- | --- |
| Small | 3/3 completed | 3/3 completed | Exact README-only change; independent checks passed. |
| Medium | 3/3 completed | 3/3 completed | Independent version checks and packaging checks passed; agents reported running focused checks. |
| Large | 0/3 completed | 0/3 completed | All six changed the existing behavior of unknown `validate.py` arguments despite the compatibility requirement. External checks added after review detect the mismatch. |

The original functional JSON evaluator, packaging checks, and generated-file
checks passed in all toolkit trials; baseline Large trial 3 had a failing
packaging test. All three toolkit Large agents stated the readiness criteria
before editing and ran a focused test suite. One explicitly retried a narrower
check after a compound command was denied. In the baseline Large trials, the
readiness gate was met twice; none completed the requested final verification.
The third toolkit agent could not run its planned side-by-side comparison of
default output after repeated denials; its added and independent tests passed.

Manual review identified a gap in the original Large evaluator: before the
change, `validate.py --unrecognized` exits 0 and runs normal validation; all six
Large solutions exit 2. The updated independent CLI check verifies that
existing behavior as well as `build.py`'s existing rejection of unknown options.
It fails for every Large candidate. These are explicit backward-compatibility
failures, even though the originally frozen external checks passed. The CSV
records the revised manual acceptance outcome; raw session summaries retain
the original check results. No security or architecture-boundary violation was
identified in the reviewed diffs.

Small median wall time was 5.118 s baseline and 3.749 s toolkit (26.7% lower).
Median measured tokens, including input, output, cache creation, and cache
reads, were 33,652 baseline and 24,855 toolkit (26.1% lower). Both measured
Small overheads fall within the proposed 20% ceiling. Three pairs are a small
pilot, not proof of broad effectiveness.

**Release gate: not met.** The previously missed CLI compatibility requirement
fails across both arms. Preserve all three pilot records, clarify this behavior
in the task and independent evaluator, and rerun affected Large scenarios before
reassessing; do not silently replace the original results.
