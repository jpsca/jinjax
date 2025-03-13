.PHONY: install
install:
	uv sync --group dev --group test
	pip install -e .
	pre-commit install

.PHONY: test
test:
	uv run pytest -x src/jinjax tests

.PHONY: lint
lint:
	uv run ruff check src/jinjax tests

.PHONY: coverage
coverage:
	uv run pytest --cov-config=pyproject.toml --cov-report html --cov jinjax src/jinjax tests

.PHONY: types
types:
	uv run pyright src/jinjax
