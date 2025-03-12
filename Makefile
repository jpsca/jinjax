.PHONY: install
install:
	uv sync --group dev --group test
	pip install -e .
	pre-commit install

.PHONY: test
test:
	pytest -x src/jinjax tests

.PHONY: lint
lint:
	ruff check src/jinjax tests

.PHONY: coverage
coverage:
	pytest --cov-config=pyproject.toml --cov-report html --cov jinjax src/jinjax tests

.PHONY: types
types:
	pyright src/jinjax
