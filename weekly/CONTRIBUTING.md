# Contributing to weekly

Thank you for your interest in contributing to weekly! We welcome contributions from the community to help improve this project.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/your-username/weekly.git
   cd weekly
   ```
3. **Set up** a development environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev]
   ```

## Development Workflow

1. Create a new branch for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests and checks
   ```bash
   make check  # Runs lint, typecheck, and tests
   ```
4. Commit your changes with a descriptive message
   ```bash
   git commit -m "Add new feature"
   ```
5. Push to your fork and create a Pull Request

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all function and method signatures
- Keep lines under 88 characters (Black's default)
- Document public functions and classes with docstrings
- Write tests for new functionality

## Testing

Run the test suite:

```bash
pytest
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
