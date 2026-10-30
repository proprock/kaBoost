# 010: Codex init skills

Status: accepted

## Decision

Give Codex the two init operations as skills, `kaboost-init` and `kaboost-init-global`, since Codex has no plugin commands ([ADR 007](007-explicit-commands.md)). Each skill sets `policy.allow_implicit_invocation: false` in `agents/openai.yaml`, so Codex runs it only on an explicit `$kaboost-init` or `$kaboost-init-global`. The build refuses a Codex skill without that policy.

The skills call the same engine as the Claude commands ([ADR 009](009-init-engine.md)), bundled in the Codex package as `init/`, with `--targets codex`. They reach the script by a path relative to their own file (`../../init/kaboost_init.py`), because Codex defines no plugin-root variable. Codex has no structured question tool, so the skills ask numbered questions in plain text.

The skills live in `adapters/codex/skills/` and are listed under `codex_skills` in `toolkit.json`; the Claude package does not receive them, and the canonical `skills` list is unchanged.

## Evidence

The documented behavior of `allow_implicit_invocation: false` is that Codex does not select the skill from the prompt while explicit `$skill` invocation still works. Package tests check the policy file, the `--targets codex` call, and that the bundled script runs from the package and writes only Codex's entries (`AGENTS.md` in the repository, `~/.codex/AGENTS.md` globally). The Codex CLI was not available for a live session, so the explicit invocation and the absence of routing noise in a real Codex session are unverified.

## Consequences

- Amends ADR 007: Codex packages gain two explicit-only skills. They still add no commands, hooks, or automatic behavior.
- Whether disabled-implicit skills add anything to the model's skill listing is unmeasured; check it in a real Codex session before the stable release (KB-213).
- Requires `python3`, as the Claude commands do.
