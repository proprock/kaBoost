## Pre-commit hooks

- Git hooks run through `prek` from `.pre-commit-config.yaml`; kaBoost init installed the hook, and `prek install` reinstalls it in a fresh clone.
- Never bypass a failing hook with `--no-verify`; fix the cause. If a hook is wrong, change the hook in its own commit.
