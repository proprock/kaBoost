# Pilot preparation (not frozen)

Candidate project: this repository, using a clean checkout of commit
`b1d3f01c9884468b8b75ec913eebb5f5ec611f1d`. No trials have been run and
this is not a release-gate result. Before choosing this project, ensure baseline
and toolkit sessions have the same existing project instructions, and that the
toolkit is activated only for the toolkit arm. Evaluator checks must be outside
the tested checkout.

## Small candidate: release tag wording

The README says a reviewed tag is immutable, but a Git tag can be moved. Ask
for a focused correction to that one sentence: describe a reviewed release tag
and checking that it still points to the expected commit, without changing
installation commands or the surrounding release status. The evaluator must
inspect the exact diff and independently judge whether the resulting wording
avoids claiming that tags cannot move. This corrects factual wording rather
than a spelling typo; it remains a one-sentence documentation task.

## Medium candidate: stable version validation

The current validator accepts `01.0.0` as a stable SemVer triple. On Linux,
this was reproduced in a temporary copy by assigning that value consistently
to `toolkit.json`, `adapters/claude-code/plugin.json`, and the marketplace
entry, rebuilding the generated package, and running `validate(root)`: it
returned 8 rather than rejecting the version. A candidate task is to reject
leading zeroes and non-ASCII digits in numeric components while preserving
valid stable `major.minor.patch` triples and rejecting prerelease/build forms
as the current contract does. Independent acceptance must cover valid zero and
multi-digit components, invalid leading zeroes in each component, non-ASCII
digits, and existing manifest/version consistency and package checks.
The independent [acceptance script](acceptance_semver.py) failed on the current
implementation for all three leading-zero positions and an Arabic-Indic digit.
It passed against a temporary copy with an ASCII, no-leading-zero version
predicate. This verifies the candidate check, not an agent trial. Run the
script from outside each trial checkout to keep its contents out of the agent's
working tree.

## Large candidate: structured results for both maintainer CLIs

Add an opt-in `--json` output mode to both `scripts/build.py` and
`scripts/validate.py`. The candidate contract is one JSON object on stdout:
`{"ok": true, "files": N}` on success and `{"ok": false, "error": "..."}`
on expected failure, with the existing nonzero exit status. Default output,
default exit codes, and callable Python APIs must remain compatible. Both
success and a broken-input failure need independent subprocess checks; no new
dependency, publication action, or changes to generated package content are
allowed. Before coding, require a short design decision and acceptance mapping
covering both entrypoints, errors, and backward compatibility.

The independent [CLI acceptance script](acceptance_json_cli.py) covers default
success, JSON success including build `--check`, and expected invalid-manifest
failure for both entrypoints. It fails on the baseline and passed against a
temporary reference implementation. Its scope does not replace review of the
actual diff, generated package consistency, tests, or architectural impact.

The Large readiness gate is met only when, before the first source or test
edit, the agent states acceptance criteria and non-goals, compares an approach
for sharing result formatting with keeping each CLI independent, chooses an
approach, and identifies success, failure, and backward-compatibility checks.
The evaluator must check the event sequence, not just the final response.

Fixed model/client configuration, permissions, budgets, exact prompts, trial
order, and a verified isolated execution procedure remain to be established
before the pilot is frozen. Do not run trials using this draft as a completed
plan.
