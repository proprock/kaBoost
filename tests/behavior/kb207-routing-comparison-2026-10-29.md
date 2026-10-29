# KB-207 routing comparison — 2026-10-29

Four uninstrumented Claude Code 2.1.312 sessions used `claude-sonnet-5-5`,
medium effort, the frozen pilot project `b1d3f01c9884468b8b75ec913eebb5f5ec611f1d`,
and the expanded pilot permissions. One Small and one Large task ran with the
prior toolkit `bd080a4187b1580ee470d090ef3d8ed7d25012f4` and the revised
toolkit `38654b36d4fd25d273fde10107e95f614e140b3f`; order alternated by
scenario. Large omitted explicit readiness instructions. See the
[comparison runner](run_routing_comparison.py) for prompts and setup. The
authenticated profile was reused, not account-isolated.

| Scenario | Previous toolkit | Revised toolkit |
| --- | --- | --- |
| Small | Independent acceptance passed; no skill or adaptive workflow call; 4.782 s. | Independent acceptance passed; no skill or adaptive workflow call; 3.561 s. |
| Large | No skill or adaptive workflow call; no stated readiness before edits; independent acceptance failed on unknown arguments. | No skill or adaptive workflow call; no stated readiness before edits; independent acceptance failed on unknown arguments. |

All four sessions exited 0, discovered the toolkit skills, retained their
source HEAD and harness files, and passed independent packaging and generated
checks. The two Large sessions each had two permission denials; neither Small
session had a denial. These independent checks do not establish agent-run
verification. The revised Large session ran the packaging suite and reported
the changed argument behavior; the previous Large session did not add tests.
Total reported cost was USD 0.2708. Raw events, diffs, session summaries,
usage and check output remain under `/tmp/kaboost-kb207-routing-compare-20261029`
and are not durable.

The revised wording did not produce an observed routing or readiness improvement
in this pair. The test does not prove why: there was no per-session core marker,
and discovery does not establish that instructions were followed. One pair per
scenario and permission denials preclude general effectiveness, overhead, or
release-gate conclusions. Prior results remain separate; KB-207 stays open.
