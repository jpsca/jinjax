.PHONY: install
install:
	uv sync --group dev --group test
	uv pip install -e .
	uv run pre-commit install

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

.PHONY: docs
docs:
	cd docs && uv run python docs.py

.PHONY: docs-build
docs-build:
	cd docs && uv run python docs.py build

.PHONY: docs-deploy
docs-deploy:
	cd docs && uv run sh deploy.sh
