# Contributing to Weekly

Thank you for your interest in contributing to Weekly! We welcome contributions from the community to help improve this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/your-username/weekly.git
   cd weekly
   ```
3. **Set up** the development environment using Poetry:
   ```bash
   # Install Poetry if you don't have it
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install project dependencies
   poetry install
   
   # Activate the virtual environment
   poetry shell
   ```

## Development Workflow

1. Create a new branch for your changes
   ```bash
   git checkout -b type/scope/description
   # Example: git checkout -b feat/cli/add-verbose-flag
   ```
   
   Branch naming conventions:
   - `feat/`: New features
   - `fix/`: Bug fixes
   - `docs/`: Documentation changes
   - `test/`: Test-related changes
   - `chore/`: Maintenance tasks

2. Make your changes following the code style guidelines

3. Run tests and checks
   ```bash
   make check  # Runs lint, typecheck, and tests
   ```
   
   Or run individual commands:
   ```bash
   make lint      # Run linters
   make typecheck # Run type checking
   make test      # Run tests
   ```

4. Commit your changes with a descriptive message following the [Conventional Commits](https://www.conventionalcommits.org/) format:
   ```bash
   git commit -m "type(scope): brief description of changes"
   # Example: git commit -m "feat(cli): add verbose flag to analyze command"
   ```

5. Push to your fork and create a Pull Request

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all function and method signatures
- Keep lines under 88 characters (Black's default)
- Document public functions and classes with docstrings following Google style
- Write tests for new functionality
- Use absolute imports
- Group imports in the following order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports

## Testing

Run the test suite:

```bash
# Run all tests with coverage
make test

# Run a specific test file
poetry run pytest tests/test_module.py

# Run tests with detailed output
poetry run pytest -v

# Run tests with coverage report
poetry run pytest --cov=weekly --cov-report=term-missing
```

## Documentation

- Keep docstrings up to date
- Update README.md for significant changes
- Add examples in the examples/ directory when adding new features
- Document any breaking changes in CHANGELOG.md

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build
2. Update the README.md with details of changes to the interface, including new environment variables, exposed ports, useful file locations, and container parameters
3. Increase the version number in pyproject.toml following [Semantic Versioning](https://semver.org/)
4. Update CHANGELOG.md with details of changes
5. Your pull request will be reviewed by the maintainers

## Reporting Issues

When opening an issue, please include:

- A clear, descriptive title
- A description of the issue
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Any relevant logs or error messages

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
```

Run with coverage:

```bash
pytest --cov=weekly --cov-report=term-missing
```

## Pull Request Guidelines

- Keep PRs focused on a single feature or bugfix
- Update documentation as needed
- Make sure all tests pass
- Add tests for new functionality
- Update the CHANGELOG.md with your changes

## Reporting Issues

When reporting issues, please include:

- A clear description of the problem
- Steps to reproduce the issue
- Expected vs. actual behavior
- Version information (Python, package version, etc.)
- Any relevant error messages or logs

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.
