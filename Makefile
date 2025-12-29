all: fmt

.PHONY: fmt
fmt:
	uv run ruff format
	uv run ruff check --fix

.PHONY: check
check:
	uv run mypy
