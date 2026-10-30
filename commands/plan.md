---
description: Plan a risky or unclear change before the first edit
argument-hint: <task>
disable-model-invocation: true
---
Use the kaboost:plan-before-edit skill for this task: $ARGUMENTS

Before the first edit, write this block in your reply, with exactly these headings, and wait for no input:

**Criteria** — what must be true when the task is done.
**Non-goals** — what you will not change.
**Must not change** — existing behavior, callers and tests that depend on it, found by reading the code.
**Alternative rejected** — one other design and why you did not choose it.
**Checks** — the commands you will run: success, failure, and compatibility.

Then implement in small verified steps and run the checks.
