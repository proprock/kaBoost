# 012: Stable release on the documented gates

Status: accepted (KB-026)

## Context

On 2026-10-30 the stable release (KB-023) was made to wait for evidence from real use of the candidate (KB-025): about twenty TDD red/green pairs mined from the maintainer's projects and compared with earlier history. The documented release gates in the [roadmap](../roadmap.md) are non-inferiority gates; improvement over baseline is explicitly not one of them ([gate assessment](../release-gate-assessment.md)). A week later KB-025 had no recorded progress: no real red/green pairs, and no defined measure of compliance or rework, nor a baseline to compare with, since earlier history has no pairs.

## Decision

Publish `v0.1.0` when the documented gates are met for the content being released, without the KB-025 evidence. The content is that of `v0.1.0-rc.3`; only documentation and the evaluation harness change. The Small-task overhead gate is measured again on that content before tagging (KB-027), because the earlier measurement predates the KB-222 and KB-218 core additions; if it fails, the release waits. Result: met on one task ([KB-027](../../tests/behavior/kb027-small-overhead-2026-11-07.md)).

The release makes no effectiveness claim. KB-025 continues as the evidence program for 0.2 and gates nothing until it has measurable criteria, a baseline window and a time box. (2026-11-08: `v0.2.0` shipped on the same gates; KB-025 continues for a later release.)

## Alternatives and tradeoffs

- **Keep waiting for KB-025:** keeps a stronger claim possible, but blocks a release that its own gates allow, on evidence that nothing is collecting.
- **Define KB-025 metrics and time-box it first:** sound for 0.2, but it delays a release whose content is unchanged since the reviewed candidate.

## Consequences

- KB-023 depends on the gates and on publication authorization only. Publication, the catalog pin in `proprock/marketplace` and installation from the published tag remain separate, authorized steps.
- The candidates and the release share the package version 0.1.0, so the move from a candidate to `v0.1.0` uses the reinstall described in [migration](../migration.md) rather than `plugin update`.
- Supersedes the "including the KB-025 evidence" condition added to KB-023 on 2026-10-30.
