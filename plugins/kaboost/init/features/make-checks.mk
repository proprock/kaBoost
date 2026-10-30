.PHONY: sync format lint type tests check

sync:
	uv sync --all-extras --group dev

format:
	uv run ruff format
	uv run ruff check --fix

lint:
	uv run ruff check

type:
	uv run ty check

tests:
	uv run pytest

check: format lint type tests
