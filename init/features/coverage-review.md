## Coverage and mutation checks

- After a substantial feature, review the coverage of the new code and add tests for uncovered behavior, not for uncovered lines.
- Run a mutation check (for example `mutmut`, `cargo-mutants`, or Stryker) only after a large change to security-relevant code: authentication, authorization, input validation, cryptography, or parsing of untrusted data. Do not run it for the rest of the project.
