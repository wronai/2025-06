.PHONY: install test lint format typecheck clean build publish

# Variables
PYTHON = python3
PIP = pip
PACKAGE = weekly

# Install the package in development mode
install:
	$(PIP) install -e .[dev]

# Run tests
test:
	pytest tests/

# Run linter
lint:
	black --check $(PACKAGE) tests/
	isort --check-only $(PACKAGE) tests/
	flake8 $(PACKAGE) tests/

# Format code
format:
	black $(PACKAGE) tests/
	isort $(PACKAGE) tests/

# Run type checker
typecheck:
	mypy $(PACKAGE) tests/

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ __pycache__/ */__pycache__/ .coverage htmlcov/

# Build package
build:
	$(PYTHON) -m build

# Publish to PyPI (requires twine)
publish: clean
	poetry version patch
	poetry build
	poetry publish

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Default target
.DEFAULT_GOAL := help
help:
	@echo "Available targets:"
	@echo "  install    - Install package in development mode"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linters (black, isort, flake8)"
	@echo "  format     - Format code"
	@echo "  typecheck  - Run type checker (mypy)"
	@echo "  check      - Run all checks (lint, typecheck, test)"
	@echo "  clean      - Remove build artifacts"
	@echo "  build      - Build package"
	@echo "  publish    - Publish to PyPI (requires twine)"
