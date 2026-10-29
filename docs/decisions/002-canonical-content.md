# 002: Canonical content and native packages

Status: accepted

## Decision

Maintain Markdown rules and minimal Agent Skills once; generate a committed native Claude bundle with a stdlib Python build.

## Alternatives and tradeoffs

Hand-maintained copies drift. A universal plugin schema hides incompatible semantics. A workflow DSL adds runtime machinery.

## Consequences

Metadata remains native, generated files are checked against sources, end users do not need Python.
