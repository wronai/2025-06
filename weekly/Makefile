.PHONY: install install-dev test lint format typecheck clean build publish check help

# Variables
PACKAGE = weekly

# Install package in development mode with all dependencies
install:
	poetry install --no-root

# Install development dependencies
install-dev:
	poetry install --with dev

# Run tests with coverage
test:
	poetry run pytest --cov=$(PACKAGE) --cov-report=term-missing tests/

# Run linter
lint:
	poetry run black --check $(PACKAGE) tests/
	poetry run isort --check-only $(PACKAGE) tests/
	poetry run flake8 $(PACKAGE) tests/

# Format code
format:
	poetry run black $(PACKAGE) tests/
	poetry run isort $(PACKAGE) tests/

# Run type checker
typecheck:
	poetry run mypy $(PACKAGE) tests/

# Clean build artifacts and cache
clean:
	poetry env remove --all 2>/dev/null || true
	rm -rf \
		.pytest_cache/ \
		.mypy_cache/ \
		.coverage \
		htmlcov/ \
		dist/ \
		build/ \
		*.egg-info/ \
		__pycache__/ \
		*/__pycache__/ \
		*/*/__pycache__/

# Build package
build:
	poetry build

# Publish to PyPI
publish: clean
	poetry version patch
	poetry build
	poetry publish

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Show help
help:
	@echo "\n\033[1mAvailable targets:\033[0m"
	@echo "  \033[36minstall\033[0m      - Install package in development mode with all dependencies"
	@echo "  \033[36minstall-dev\033[0m  - Install development dependencies"
	@echo "  \033[36mtest\033[0m         - Run tests with coverage"
	@echo "  \033[36mlint\033[0m         - Run linters (black, isort, flake8)"
	@echo "  \033[36mformat\033[0m       - Format code (black, isort)"
	@echo "  \033[36mtypecheck\033[0m    - Run static type checking (mypy)"
	@echo "  \033[36mclean\033[0m        - Remove build artifacts and cache"
	@echo "  \033[36mbuild\033[0m        - Build package"
	@echo "  \033[36mpublish\033[0m      - Publish package to PyPI"
	@echo "  \033[36mcheck\033[0m        - Run all checks (lint, typecheck, test)"
	@echo "  \033[36mhelp\033[0m         - Show this help message\n"

# Default target
.DEFAULT_GOAL := help
	@echo "  install    - Install package in development mode"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linters (black, isort, flake8)"
	@echo "  format     - Format code"
	@echo "  typecheck  - Run type checker (mypy)"
	@echo "  check      - Run all checks (lint, typecheck, test)"
	@echo "  clean      - Remove build artifacts"
	@echo "  build      - Build package"
	@echo "  publish    - Publish to PyPI (requires twine)"
