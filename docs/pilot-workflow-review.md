# Pilot evidence and workflow expansion

Reviewed 2026-10-29 for KB-201. This review identifies candidate gaps before
expanding the catalog; it does not claim that a new skill fixes them. The
existing catalog contains project-context, systematic-debugging, and
verification. No new skill is added by this review.

| Candidate | Observed gap and evidence | Decision for subsequent work |
| --- | --- | --- |
| Requirements and task-workflow references (KB-202) | The [shared Large scenario](../tests/behavior/codex-comparison-results-2026-10-29.md) missed an existing CLI compatibility contract in all six trials for each client, despite a general compatibility requirement. | Consider a compact prompt to identify existing contracts and acceptance checks; validate it on a scenario where the contract must be discovered, not merely supplied. Branch and handoff guidance address workflow needs, not demonstrated pilot failures. |
| Architecture review (KB-203) | The [original pilot](../tests/behavior/pilot-results-2026-10-29.md) missed pre-edit readiness in two toolkit Large trials. No critical architecture-boundary violation was identified. | A readiness gap is observed, but a separate architecture skill is not justified by a demonstrated boundary failure. Evaluate added value against the existing core and defer if unsupported. |
| TDD (KB-204) | In the [initial pilot](../tests/behavior/pilot-results-2026-10-29.md), some positive-version tests were weak, Large packaging tests failed in three trials across both arms, and one toolkit Large trial added no tests. | Evaluate focused regression and contract-test guidance against existing verification; test whether it improves independent test adequacy before adding a skill. |
| Independent code review (KB-205) | Manual review of the [follow-up](../tests/behavior/pilot-followup-results-2026-10-29.md) found the compatibility regression missed by the original evaluator. | Assess independent review as a candidate for finding missed contracts; the pilot does not prove that a dedicated review skill would have found it. |
| Separate requirements and task-workflow skills (KB-206) | The pilot shows a contract-discovery gap, but does not compare skill boundaries or demonstrate a need for two separate skills. | Decide after evaluating compact references and routing; merge or defer if separation adds no demonstrated value. |

The [clarified-contract retest](../tests/behavior/pilot-compatibility-results-2026-10-29.md)
passed the expanded compatibility check in all six trials, but only one of
three toolkit trials met the complete pre-edit readiness gate. Supplying the
contract is not evidence of discovering it. Permission denials, small sample
sizes, changing retest conditions, and temporary raw logs limit causal and
long-term audit conclusions. The P0 release gate remains not met; KB-018
retains responsibility for assessment and affected reruns.

Before adding a candidate, document its specific gap, why existing content is
insufficient, and an independent behavior check with matched conditions.
Preserve prior results and measure Small-task overhead as well as the intended
benefit. If the evidence does not support a separate skill, record a merge or
deferral instead of expanding the catalog for completeness.
