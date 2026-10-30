---
name: kaboost-coverage-improvement
description: Find untested behavior in the changed code and add tests that can fail for a real defect.
---
# Coverage improvement

1. Run the project's coverage command on the tests for the changed files and list the uncovered branches and error paths.
2. Pick the ones that carry behavior: error handling, boundaries, and state changes. Skip trivial lines.
3. For each, write one focused test per scenario that fails when the behavior is wrong; confirm it fails against a deliberate break, then restore the code.
4. Keep tests deterministic and isolated. Do not change production code to raise a number.
5. Report the behavior now covered, what is still uncovered and why, and the commands run.
