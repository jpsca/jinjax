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

.PHONY: install
install:
	poetry install --with dev,test
	pre-commit install

.PHONY: docs
docs:
	cd docs && python docs.py

.PHONY: docs.build
docs.build:
	cd docs && python docs.py build
