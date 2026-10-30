---
name: systematic-debugging
description: Find the root cause of non-trivial bugs, regressions, flaky tests, and unexplained failures using evidence and controlled experiments. Skip for obvious text-only corrections.
---
# Systematic debugging

1. Establish expected behavior and a reproducible failure. Capture the command, inputs, environment, and observed result. If reproduction is unavailable, state the limit and gather the smallest relevant evidence.
2. Trace the failing path and its contracts. Inspect recent changes and working-tree state without assuming the newest change caused the failure.
3. State a falsifiable hypothesis with a predicted observation. Run the smallest safe experiment that distinguishes it from alternatives; change one relevant variable at a time.
4. Update the hypothesis from evidence. After two experiments with no progress, revisit reproduction, boundaries, and assumptions before trying another patch. Escalate a missing external prerequisite explicitly.
5. Correct the cause with a focused change. Where practical, first add a behavioral regression test and observe it fail for the expected reason. Do not mask errors, weaken assertions, or add retries without evidence that retrying is the intended contract.
6. Reproduce again, run the regression test and relevant neighboring checks, and inspect the diff for unintended changes.

Return the cause, supporting evidence, correction, verification results, and remaining uncertainty. A passing isolated test alone does not prove the whole system is fixed. Do not add mandatory tools, logging frameworks, or mutation testing.
