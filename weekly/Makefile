# Define colors for better output
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

# Project information
PACKAGE = weekly
PYTHON = poetry run python
PIP = poetry run pip
PYTEST = poetry run pytest
MYPY = poetry run mypy
BLACK = poetry run black
ISORT = poetry run isort
FLAKE8 = poetry run flake8
COVERAGE = poetry run coverage

# Default target
.DEFAULT_GOAL := help
.PHONY: help install install-dev test test-cov lint format format-check typecheck \
        clean build publish check docs serve pre-commit bump-version safety dep-update \
        info release

# Help target with colored output
## Show this help message
help:
	@echo ""
	@echo "${YELLOW}Usage:${RESET} make ${GREEN}<target>${RESET}"
	@echo ""
	@echo "${YELLOW}Available targets:${RESET}"
	@echo "  ${GREEN}install${RESET}       - Install package in development mode with all dependencies"
	@echo "  ${GREEN}install-prod${RESET}   - Install only production dependencies"
	@echo "  ${GREEN}test${RESET}          - Run tests"
	@echo "  ${GREEN}test-cov${RESET}      - Run tests with coverage report"
	@echo "  ${GREEN}lint${RESET}          - Run all linters (black, isort, flake8)"
	@echo "  ${GREEN}format${RESET}        - Format code"
	@echo "  ${GREEN}format-check${RESET}  - Check code formatting"
	@echo "  ${GREEN}typecheck${RESET}     - Run static type checking"
	@echo "  ${GREEN}check${RESET}         - Run all checks (lint, format-check, typecheck, test)"
	@echo "  ${GREEN}clean${RESET}         - Remove build artifacts and cache"
	@echo "  ${GREEN}build${RESET}         - Build package"
	@echo "  ${GREEN}publish${RESET}       - Publish package to PyPI"
	@echo "  ${GREEN}docs${RESET}          - Build documentation"
	@echo "  ${GREEN}serve${RESET}         - Serve documentation locally"
	@echo "  ${GREEN}pre-commit${RESET}    - Install pre-commit hooks"
	@echo "  ${GREEN}bump-version${RESET}  - Bump version (make bump-version PART=patch)"
	@echo "  ${GREEN}safety${RESET}        - Check for security vulnerabilities"
	@echo "  ${GREEN}dep-update${RESET}    - Update dependencies"
	@echo "  ${GREEN}info${RESET}          - Show package information"
	@echo "  ${GREEN}release${RESET}       - Create a new release (tag and publish)"
	@echo "  ${GREEN}help${RESET}          - Show this help message"

## Install package in development mode with all dependencies
install:
	@echo "${YELLOW}Installing package in development mode...${RESET}"
	poetry install --with dev

## Install only production dependencies
install-prod:
	@echo "${YELLOW}Installing production dependencies...${RESET}"
	poetry install --only main

## Run tests
##   ARGS: Additional arguments to pass to pytest (e.g., make test ARGS="-k test_name")
test:
	@echo "${YELLOW}Running tests...${RESET}"
	${PYTEST} -v $(ARGS) tests/

## Run tests with coverage report
test-cov:
	@echo "${YELLOW}Running tests with coverage...${RESET}"
	${PYTEST} -v --cov=${PACKAGE} --cov-report=term-missing --cov-report=xml --cov-report=html tests/

## Run linters
lint:
	@echo "${YELLOW}Running linters...${RESET}"
	${BLACK} --check ${PACKAGE} tests/
	${ISORT} --check-only ${PACKAGE} tests/
	${FLAKE8} ${PACKAGE} tests/

## Format code
format:
	@echo "${YELLOW}Formatting code...${RESET}"
	${BLACK} ${PACKAGE} tests/
	${ISORT} ${PACKAGE} tests/

## Check code formatting without making changes
format-check:
	@echo "${YELLOW}Checking code formatting...${RESET}"
	${BLACK} --check ${PACKAGE} tests/
	${ISORT} --check-only ${PACKAGE} tests/

## Run type checking
typecheck:
	@echo "${YELLOW}Running type checking...${RESET}"
	${MYPY} ${PACKAGE} tests/

## Run all checks (lint, format-check, typecheck, test)
check: lint format-check typecheck test

## Clean build artifacts and cache
clean:
	@echo "${YELLOW}Cleaning...${RESET}"
	rm -rf \
		.pytest_cache/ \
		.mypy_cache/ \
		.coverage \
		.coverage.* \
		coverage.xml \
		htmlcov/ \
		dist/ \
		build/ \
		*.egg-info/ \
		__pycache__/ \
		*/__pycache__/ \
		*/*/__pycache__/ \
		.python-version \
		.mypy_cache \
		.pytest_cache \
		.eggs \
		.tox

## Build package
build:
	@echo "${YELLOW}Building package...${RESET}"
	poetry build

## Publish package to PyPI
publish:
	#@echo "${YELLOW}Publishing to PyPI...${RESET}"
	poetry version patch
	poetry publish --build


## Build documentation
docs:
	@echo "${YELLOW}Building documentation...${RESET}"
	cd docs && poetry run make html

## Serve documentation locally
serve:
	@echo "${YELLOW}Serving documentation at http://localhost:8000${RESET}"
	cd docs/_build/html && python -m http.server

## Install pre-commit hooks
pre-commit:
	@echo "${YELLOW}Installing pre-commit hooks...${RESET}"
	poetry run pre-commit install

## Bump version (e.g., make bump-version PART=patch)
bump-version:
	@if [ -z "$(PART)" ]; then \
		echo "${YELLOW}Error: PART variable not set. Usage: make bump-version PART=<major|minor|patch>${RESET}"; \
		exit 1; \
	fi
	@echo "${YELLOW}Bumping $(PART) version...${RESET}"
	poetry version $(PART)
	git add pyproject.toml
	git commit -m "Bump version to $(shell poetry version -s)"
	git tag -a v$(shell poetry version -s) -m "Version $(shell poetry version -s)"
	@echo "${GREEN}Version bumped to $(shell poetry version -s)${RESET}"

## Run safety check for known security vulnerabilities
safety:
	@echo "${YELLOW}Checking for security vulnerabilities...${RESET}"
	poetry run safety check --full-report

## Run dependency updates
dep-update:
	@echo "${YELLOW}Updating dependencies...${RESET}"
	poetry update

## Show package information
info:
	@echo "${YELLOW}Package Information:${RESET}"
	@poetry version
	@echo "\n${YELLOW}Dependencies:${RESET}"
	@poetry show --tree

## Create a new release
release: check build
	@echo "${YELLOW}Creating release...${RESET}"
	git push origin main --tags
	poetry publish --build
