---
description: Show which kaBoost command fits the task at hand
argument-hint: [task description]
disable-model-invocation: true
---
Explain briefly which kaBoost command fits this situation: $ARGUMENTS

| Situation | Command |
| :- | :- |
| Typo, docs, or one-line local fix | none; just make the change |
| Adds or changes a CLI flag, output format, public API, schema, config, or security behavior; scope unclear | `/kaboost:plan <task>` before the first edit |
| A test fails or behavior regressed | `/kaboost:debug <symptom>` |
| Done with a change; check it against its criteria | `/kaboost:verify [criteria]` |
| New to the repository, resuming stale work, or handing off | `/kaboost:context [topic]` |

Skills also load on their own from their descriptions; the commands make the choice explicit. If a task description was given, name the one command that fits and why. Otherwise show the table.
