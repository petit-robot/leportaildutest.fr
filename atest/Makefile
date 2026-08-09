file := .

.PHONY: all install lint format robocop-lint robocop-format docstrfmt sphinxlint

all: format docstrfmt robocop-format lint robocop-lint sphinxlint

install:
	pip install -r requirements-dev.txt

lint:
	ruff check --fix $(file)

format:
	ruff format $(file)

robocop-lint:
	robocop check $(file)

robocop-format:
	robocop format $(file)

docstrfmt:
	# Should use these options because pyproject.toml isn't at the root folder (same as .git)
	docstrfmt --ignore-cache --pyproject-config pyproject.toml $(file)

sphinxlint:
	sphinx-lint --max-line-length 120 $(file)
