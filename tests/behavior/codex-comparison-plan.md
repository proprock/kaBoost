# Cross-client behavior comparison — 2026-10-29

Compare Codex CLI 0.165.0, model `gpt-6.1-sol`, medium reasoning, with the
existing Claude Code 2.1.312 / `claude-sonnet-5-5` [follow-up trials](pilot-followup-results-2026-10-29.md).
Both use the original Small, Medium, and Large prompts and independent checks in
the [frozen plan](pilot-plan.md), the same project commit and canonical toolkit
content. Do not use the later Large prompt clarification. The updated Large
acceptance check catches the previously missed unknown-argument contract.

For Codex, use three baseline/toolkit pairs per scenario with alternating arm
order, a fresh checkout and ephemeral session per arm. The baseline removes the
toolkit plugin from the temporary profile; the toolkit arm installs it and instructs Codex via a project
`AGENTS.md` to read a project-local copy of core rules. Keep setup files excluded
from the trial diff and check they are unchanged. The authenticated temporary
Codex profile is reused, so this is not account-level isolation. Check discovery
through `skills/list` for each arm. A CLI configuration override did not hide
installed skills from that list in preflight, so it is not used for baseline
isolation. Existing built-in
skills remain available. The client uses workspace-write sandbox and never asks
for approvals. Each session has a 10-minute timeout; Codex CLI does not expose
the Claude per-session USD limit, so cost is not inferred from token counts.

Capture event streams and diffs locally under `/tmp`, run independent acceptance,
existing package tests and generated-file checks, and manually review each diff
and the Large pre-edit readiness gate. Treat missing events or a timeout as
unassessed or failed, not a pass. Do not infer agent-run checks from independent
checks. Models, client permission systems, plugin mechanisms, and execution
times differ; this is a descriptive cross-client comparison, not an isolated
estimate of model or toolkit effect and not a replacement for the P0 release
gate. Results and failures remain separate from prior trials.
