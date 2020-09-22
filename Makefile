NAME=$(shell basename $(PWD))

PYTHON:=3.8

.PHONY: pytest
pytest:
	poetry run pytest -vs ${ARGS}

.PHONY: black
black:
	poetry run black --check .

.PHONY: pylama
pylama:
	poetry run pylama

.PHONY: mypy
mypy:
	poetry run mypy .

.PHONY: tests
tests: black pylama mypy pytest

.PHONY: docs
docs:
	rm -rf docs/html
	make -C docs html
	cp -a docs/build/html docs
