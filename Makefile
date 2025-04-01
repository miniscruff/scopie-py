.ONESHELL:
.DEFAULT: help

.PHONY: help
help:
	@grep -E '^[a-z-]+:.*#' Makefile | \
		sort | \
		while read -r l; do printf "\033[1;32m$$(echo $$l | \
		cut -d':' -f1)\033[00m:$$(echo $$l | cut -d'#' -f2-)\n"; \
	done

.PHONY: sync
sync: # Sync requirements.in and requirements.txt
	pip-compile --generate-hashes requirements.in

.PHONY: install
install: # Install python packages
	pip install -r requirements.txt

.PHONY: test
test: # Run unit test suite
	pytest --benchmark-disable

.PHONY: bench
bench: # Run benchmark test suite
	pytest --benchmark-enable

.PHONY: format
format: # Run linter and formatters
	black .

.PHONY: docs-build
docs-build: # Build sphinx docs as standalone files
	sphinx-build docs docs/_build
