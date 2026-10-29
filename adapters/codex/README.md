# Codex adapter

Run `python scripts/build_codex.py` from the repository root to generate the
package in `adapters/codex/package/ai-dev-toolkit`; use `--check` to detect
drift. The package contains both the Agent Plugins manifest and a Codex
compatibility manifest. Skills and the referenced workflow are copied from
the canonical sources, and the checksum inventory covers the package files.
The build does not change client configuration or delete unexpected files.

The included core rules are reference material; packaging them does not
activate them. Installation, activation, precedence, lifecycle, and discovery
in Codex remain unverified and are tracked separately in TODO.md. This package
is unreleased and should not be treated as a supported client installation.
