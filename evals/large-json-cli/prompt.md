---
max_turns: 14
allowed_tools: [Read, Glob, Grep, Edit, Write, Skill]
tags: [routing, large]
runs: 3
---

Add an opt-in --json flag to both scripts/build.py and scripts/validate.py. On success emit one JSON object on stdout with ok: true and files equal to the count; on expected failure emit one JSON object on stdout with ok: false and a nonempty error, and retain the existing nonzero exit status. Preserve existing default output and exit codes, build.py --check, and Python APIs; do not introduce dependencies or alter generated package content. Implement and run focused checks.
