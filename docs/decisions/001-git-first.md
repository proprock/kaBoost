# 001: Git-first distribution

Status: accepted

## Decision

Use reviewed Git releases and native client installation.

## Alternatives and tradeoffs

One universal marketplace would couple us to client semantics; a custom registry adds an unnecessary service. Independent skill copies alone do not provide native package lifecycle.

## Consequences

Each client needs a small delivery adapter; distribution never implies configuration sync.
