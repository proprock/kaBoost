# Codex and Claude shared behavior scenarios — 2026-10-29

The [comparison plan](codex-comparison-plan.md) ran 18 Codex sessions against
the same project commit, prompts, canonical toolkit content, and independent
checks as the earlier 18 Claude [follow-up sessions](pilot-followup-results-2026-10-29.md).
See [Codex measurements](codex-comparison-results-2026-10-29.csv). Claude and
Codex use different models, permission systems, and client configuration; these
results do not isolate a cause or prove one client generally better.

| Scenario | Claude baseline / toolkit | Codex baseline / toolkit | Review |
| --- | --- | --- | --- |
| Small | 3/3 / 3/3 | 3/3 / 3/3 | Exact requested README change. |
| Medium | 3/3 / 3/3 | 3/3 / 3/3 | Independent boundary and packaging checks passed. All six Codex agents ran the packaging suite. |
| Large | 0/3 / 0/3 | 0/3 / 0/3 | All six Codex candidates, like all six Claude candidates, changed the existing unknown-argument behavior of `validate.py`; the independent compatibility check failed. |

The six Codex Large agents stated acceptance criteria, non-goals, an alternative
and decision, and success/failure/compatibility checks before the first edit;
all ran a passing packaging suite. These checks did not cover the unknown
argument contract. All Codex runs passed the separate existing package and
generated-file checks, completed without manual intervention, kept the source
HEAD and harness files unchanged, and had the expected toolkit skill discovery
state. All toolkit runs read the project-local core file. Review included the
new untracked test file in Large baseline trial 2, which ordinary `git diff`
omits. No unrelated changes were identified in the reviewed trial diffs.
Five toolkit sessions attempted to create a feature branch in their disposable
checkout; each Git operation failed because the sandbox could not write the
Git refs. One compound shell command nevertheless returned zero because a
subsequent `cat` succeeded. No branch was created in those attempts. This is a
client-permission difference and a limitation of using the overall shell exit
code to identify individual command failures.

Codex Small median wall time was 10.831 s baseline and 11.223 s toolkit;
median input plus output tokens were 44,412 and 46,376, respectively. Input
counts include cached input. Claude's corresponding measurements are in its
separate report and use its own token accounting. Small overhead in these
Codex pairs was 3.6% in time and 4.4% in tokens, below the pilot's 20%
threshold; three pairs are insufficient to establish general performance.
Codex reported usage but not a comparable per-session monetary cost; no cost
was estimated.

The original Large prompt required default compatibility but did not name the
unknown-argument behavior. The earlier Claude compatibility retest explicitly
clarified it and is a different experiment, not silently substituted here.
The shared Large acceptance failure means the P0 release gate remains **not
met**. These outcomes are separate from the P0 gate and do not establish Codex
support on other operating systems or clients. The temporary raw event streams,
trial checkouts, and evaluator outputs are at
`/tmp/kaboost-codex-comparison-20261029` and are not durable.
