NAME=$(shell basename $(PWD))

PYTHON:=3.8

.PHONY: pytest
pytest:
	uv run pytest -vs ${ARGS}

.PHONY: black
black:
	uv run black --check .

.PHONY: pylama
pylama:
	uv run pylama

.PHONY: mypy
mypy:
	uv run mypy .

.PHONY: tests
tests: black pylama mypy pytest

.PHONY: docs
docs:
	rm -rf docs/html
	make -C docs html
	cp -a docs/build/html docs
