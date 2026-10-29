# Frozen behavior pilot plan — 2026-10-29

Project and toolkit source: kaBoost commit `b1d3f01c9884468b8b75ec913eebb5f5ec611f1d`.
The evaluator scripts and this plan are outside that commit and must not be
copied into trial checkouts. Each trial uses a fresh independent clone at that
commit and a fresh non-persistent Claude session. No trial starts from another
trial's result. No publication, network tools, external services, or secrets are
needed for the task itself.

Client: Claude Code 2.1.312; model: `claude-sonnet-5-5`; effort: `medium`;
Linux. Maximum budget per session is USD 0.40, including failed sessions; 18
sessions therefore have a configured ceiling of USD 7.20. Record actual usage
and costs separately, including cache creation and cache reads. A budget stop,
unavailable measurement, or missing trial is not a pass. Timing includes the
client process from start to exit, excluding clone and evaluator setup.

Both arms use the same authenticated profile with `--setting-sources
project,local`, `--strict-mcp-config`, `--no-session-persistence`, and identical
tool permissions: Read, Edit, Write, Glob, Grep, Skill, and Bash commands
beginning with `python3` or `git`; other permission prompts are denied. The
baseline uses the project's existing instructions, without toolkit activation.
The toolkit arm additionally imports the frozen core through a project-local
copy and loads the frozen plugin with `--plugin-dir`. Harness-owned instruction
files are ignored by Git and must be checked for unexpected changes. A preflight
with the selected setting sources showed no `ai-dev-toolkit` skills in baseline;
each trial must check initialization for contamination and expected loading.
Client built-in components remain available in both arms.

For each scenario run three paired trials; arm order is baseline/toolkit for
trial 1, toolkit/baseline for trial 2, baseline/toolkit for trial 3. Fix the
same prompt, source, model, permissions, budget, and checks for both arms. Save
sanitized JSON event streams, evaluator outcomes, working-tree diffs, durations,
usage, and manual interventions outside trial checkouts. Verify baseline has no
toolkit skill and toolkit arm has all three. Abort or mark an arm invalid if the
actual client/model or source differs, isolation fails, or an extra methodology
is activated. Do not silently rerun a failed attempt as if it were the first.

## Prompts and acceptance

**Small:** In README.md replace exactly `After a release is published, pin the
marketplace to its immutable reviewed tag.` with `After a release is published,
pin the marketplace to a reviewed tag and verify that it points to the expected
commit.` Make no other changes. Acceptance: external `acceptance_readme.py`,
review of scope and process, and no unrelated files.

**Medium:** The validator says it accepts stable SemVer triples, but accepts
leading zeroes and non-ASCII digits in version components. Correct the version
validation to accept only ASCII stable major.minor.patch numeric components
with no leading zeroes except the single digit zero. Preserve the existing
rejection of prerelease and build suffixes and existing package consistency
checks. Add a focused regression test and run the relevant checks. Acceptance:
external `acceptance_semver.py`, existing packaging tests, focused review of
the regression test and diff, and no weakened validations.

**Large:** Add an opt-in `--json` flag to both `scripts/build.py` and
`scripts/validate.py`. On success emit one JSON object on stdout with `ok: true`
and `files` equal to the count; on expected failure emit one JSON object on
stdout with `ok: false` and a nonempty `error`, and retain the existing nonzero
exit status. Preserve existing default output and exit codes, `build.py --check`,
and Python APIs; do not introduce dependencies or alter generated package
content. Before any source or test edit, state acceptance criteria and
non-goals, compare sharing the formatter with independent CLI implementations,
choose one, and identify success, failure, and compatibility checks. Implement
and run focused checks. Acceptance: external `acceptance_json_cli.py`, existing
packaging tests and generated-package check, diff and tests review, and the
readiness gate below.

## Large readiness gate

Before the first source or test edit, the event stream must contain the agent's
acceptance criteria and non-goals, a comparison of the two implementation
options, its selected approach, and planned success, failure, and compatibility
checks. A final explanation after editing cannot satisfy this gate. Failure or
missing event evidence is recorded as a failed or unassessed gate, not inferred
from the final answer.

The evaluator scripts were checked against the baseline and temporary reference
changes. Small baseline fails and the exact intended change passes; Medium
baseline fails on leading-zero and non-ASCII cases and a temporary correction
passes; Large baseline lacks JSON mode and a temporary reference passes. These
are evaluator checks, not trial results. Release thresholds and recording rules
remain those in [the evaluation protocol](README.md).
