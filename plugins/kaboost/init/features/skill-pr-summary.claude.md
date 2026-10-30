---
name: kaboost-pr-summary
description: Write a pull request description from the actual diff and test results.
disable-model-invocation: true
---
# Pull request summary

Write the description from `git diff` against the target branch and the commits, not from memory of the conversation.

- Start with what changes and why, in a few sentences; link the task or issue.
- List the checks that were run with their outcomes, and say plainly which were not run.
- Name the risks, compatibility effects, and what a reviewer should look at first.
- Follow the repository's pull request template when one exists.
- Do not describe changes that are not in the diff, and do not claim CI or another platform passed unless you saw it.
