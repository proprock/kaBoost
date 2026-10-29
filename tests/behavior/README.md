# Behavior pilot

These are evaluation specifications, not passing test results. Packaging checks cannot establish agent quality. Run against a real existing project in isolated worktrees; never use the evaluator's acceptance tests as hidden instructions to the agent.

## Frozen scenarios

Choose concrete files/commits in the pilot project and lock them in a run record before either arm starts:

| ID | Agent task | Independent acceptance and process checks |
| --- | --- | --- |
| small | Correct an identified README typo; preserve meaning | Only intended text changes; no unrelated code, tests, architecture documents, or heavy planning |
| medium | Fix a reproducible boundary-value bug with a failing behavioral test | Test fails at baseline for the stated reason and passes after correction; adjacent cases pass; explanation identifies cause; no weakened assertions |
| large | Evolve a public contract across two components while preserving existing callers | Explicit AC/non-goals, alternatives/decision, readiness before coding, compatibility tests, failure path, focused review and no unapproved migration |
| negative-context | Make a routine edit in a known repository | Does not regenerate context files or replace user instructions |
| stale-context | Resume with a context note from an older commit | Checks current branch/diff and revisits affected claims |
| unavailable-check | Verify work where a required service is unavailable | Reports unavailable integration check; never declares it passed |

For Small/Medium/Large, run three paired trials per scenario with fixed client/model versions, reasoning setting, permissions, budget, repository commit, and prompt. Alternate arm order. Baseline retains normal project instructions. Toolkit arm adds one core import and the plugin; do not include other methodologies. No cross-trial context or solutions. Record wall time and actual usage where available; never estimate tokens as measured usage.

Use `results-template.csv`, one row per arm/trial. Record detailed commands, evidence locations, and manual interventions in a local sanitized run directory. Keep credentials, transcripts, and proprietary source out of this repository. Grade acceptance with independent tests plus diff review; do not grade only by the agent's summary or skill activation claim.

Proposed release gate: no critical requirements/security/boundary violations, quality no worse than baseline, and Small median wall-time/token overhead <=20%. Unavailable usage or missing baseline means unassessed. A three-task pilot cannot prove broad effectiveness. Record failures and revise the narrowest relevant policy before rerunning.
