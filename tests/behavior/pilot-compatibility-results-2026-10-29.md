# Large CLI compatibility retest — 2026-10-29

Six isolated sessions ran under the [compatibility retest plan](pilot-compatibility-plan.md).
All six passed the expanded external CLI compatibility check and generated
package check; the independent packaging suite failed in baseline trial 3.
[Per-arm results](pilot-compatibility-results-2026-10-29.csv) record the
measurements and local evidence paths. Raw events and checkouts are under
`/tmp/kaboost-pilot-compatibility-20261029` and are not durable. Actual
reported model cost was USD 0.7648; no human intervened during a session.

Both groups received an explicit description of the previously missed
unknown-argument contract, so these results demonstrate handling of a stated
contract, not independent discovery of that contract. All three toolkit agents
ran focused tests; all three baseline agents left final checks unrun. However,
the readiness gate was satisfied before editing in baseline trials 1 and 2,
and toolkit trial 2 only. Toolkit trials 1 and 3 did not state the required
criteria, non-goals, alternatives, decision, and checks before the first edit.
Thus **one of three toolkit Large trials fully met the recorded requirements**;
the other two failed the readiness requirement despite passing external tests.

**Release gate: not met.** Large readiness remains unreliable and was worse
than baseline in this retest (1/3 versus 2/3). The original, first retest,
second retest, and this clarified-contract run must all remain visible; the
success of the expanded evaluator cannot erase prior compatibility failures.
Three trials are insufficient to establish broad effectiveness, and repeated
policy revisions and retests further limit statistical interpretation.
