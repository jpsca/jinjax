.PHONY: test
test:
	poetry run pytest -x -vv src/jinjax tests

.PHONY: lint
lint:
	poetry run flake8 src/jinjax tests

.PHONY: coverage
coverage:
	poetry run pytest --cov-config=pyproject.toml --cov-report html --cov jinjax src/jinjax tests

.PHONY: types
types:
	poetry run pyright src/jinjax

.PHONY: install
install:
	poetry install --with dev,test
	poetry run pre-commit install

.PHONY: docs
docs:
	cd docs && python docs.py

.PHONY: docs.build
docs.build:
	cd docs && python docs.py build
