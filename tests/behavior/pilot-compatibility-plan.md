# Large CLI compatibility retest — 2026-10-29

The [second retest](pilot-followup-results-2026-10-29.md) identified an
evaluator gap: all Large solutions changed `validate.py`'s behavior for
unknown arguments, despite the default-compatibility requirement. The updated
[independent check](acceptance_json_cli.py) fails against all six previous
Large solutions and passes a temporary reference that preserves the behavior.

Repeat only Large: three baseline/toolkit pairs, same source, toolkit commit,
client, model, effort, permissions, budget, arm order, readiness gate, and
isolation as the [second retest plan](pilot-followup-plan.md). Append this
explicit clarification to the frozen Large prompt for both arms: "Before the
change, validate.py ignores unknown arguments while build.py rejects them;
preserve that behavior for invocations without --json." Use the updated
external evaluator. This tests compliance when the previously missed contract
is explicit; it does not establish that agents independently discover all
compatibility requirements. Preserve prior runs and report this prompt change.

The configured maximum is six sessions at USD 0.40 each. Report readiness,
actual agent-run checks, independent tests, permission denials, usage, time,
compatibility, and any remaining failures before reassessing the release gate.
