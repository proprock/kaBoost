# Miss log

Real cases where an agent working with kaBoost made a mistake that a candidate skill or rule should have caught ([ADR 013](../../docs/decisions/013-cost-per-pass-and-miss-log.md)). Two or more misses of one kind trigger adding that candidate as an opt-in and checking it on these cases. Record facts only; name a private repository as "private" and keep personal data and secrets out.

`python scripts/kaboost_miss_candidates.py <range> --cwd <repository>` lists possible entries from git history; copy a row here only after confirming it.

Candidates so far: architecture review (KB-203), TDD skill (KB-204), code review (KB-205); add others as misses point to them.

| Date | Repository | Task | What went wrong | How it was found | Candidate |
| --- | --- | --- | --- | --- | --- |
| 2026-11-10 | aHerald | AH-297 | PR #178 was squash-merged (`c76c509`), so its code reached `master` without a red/green pair | KB-250 candidate script, confirmed by the maintainer on 2026-11-20 | tdd-commits (prevention: KB-256) |
