.DEFAULT_GOAL := all

.PHONY: install
install:
	python -m pip install -r requirements.txt

.PHONY: build
build:
	python -m pip install -e .

.PHONY: format
format:
	isort flaked tests
	black flaked tests

.PHONY: format-diff
format-diff:
	isort --check --diff flaked tests
	black --check --diff flaked tests

.PHONY: mypy
mypy:
	mypy flaked

.PHONY: lint
lint: format-diff
	flake8 flaked tests

.PHONY: test
test:
	pytest tests/

.PHONY: all
all: lint mypy test

.PHONY: clean
clean:
	git clean -f -X -d

.PHONY: docs
docs:
	flake8 --max-line-length=120 docs/examples/
	python docs/build/main.py
	mkdocs build

.PHONY: docs-serve
docs-serve:
	python docs/build/main.py
	mkdocs serve
