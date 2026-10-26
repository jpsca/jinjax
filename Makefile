.PHONY: install
install:
	uv sync --all-groups
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
	uv run ty check src/jinjax

.PHONY: docs
docs:
	cd docs && uv run python docs.py run

.PHONY: docs-build
docs-build:
	rm -rf docs/build
	cd docs && uv run python docs.py build --llm

.PHONY: docs-deploy
docs-deploy:
	cd docs && uv run sh deploy.sh
