## Python tooling

- Manage dependencies with `uv` and run every Python command through `uv run`; do not call `pip` directly.
- Format and lint with `ruff`, type-check with `ty`, and test with `pytest`.
- If `uv` fails on its cache inside a sandbox, point `UV_CACHE_DIR` at a writable directory or run the tool from the project's `.venv/bin`.
- Standalone scripts declare their dependencies with PEP 723 inline metadata.
