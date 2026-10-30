## Pre-commit hooks

- Git hooks run through `prek` from `.pre-commit-config.yaml`; install them once with `uv run prek install`.
- Never bypass a failing hook with `--no-verify`; fix the cause. If a hook is wrong, change the hook in its own commit.
