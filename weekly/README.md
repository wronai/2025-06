# Weekly - Project Quality Analyzer

[![PyPI](https://img.shields.io/pypi/v/weekly)](https://pypi.org/project/weekly/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/weekly)](https://pypi.org/project/weekly/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Versions](https://img.shields.io/pypi/pyversions/weekly.svg)](https://pypi.org/project/weekly/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![codecov](https://codecov.io/gh/wronai/weekly/branch/main/graph/badge.svg?token=YOUR-TOKEN-HERE)](https://codecov.io/gh/wronai/weekly)
[![Build Status](https://github.com/wronai/weekly/actions/workflows/tests.yml/badge.svg)](https://github.com/wronai/weekly/actions)
[![Documentation Status](https://readthedocs.org/projects/weekly/badge/?version=latest)](https://weekly.readthedocs.io/en/latest/?badge=latest)

Weekly is a comprehensive Python project quality analyzer that helps developers maintain high code quality by automatically detecting issues and suggesting improvements. It analyzes various aspects of your Python projects and generates actionable reports.

## Features

- 🧪 **Test Coverage Analysis**: Check test coverage and test configuration
- 📚 **Documentation Check**: Verify README, LICENSE, CHANGELOG, and API docs
- 🔄 **CI/CD Integration**: Detect CI/CD configuration and best practices
- 📦 **Dependency Analysis**: Identify outdated or vulnerable dependencies
- 🛠️ **Code Quality**: Check for code style, formatting, and common issues
- 📊 **Interactive Reports**: Generate detailed reports in multiple formats (JSON, Markdown, Text)
- 🔍 **Extensible Architecture**: Easy to add custom checkers and rules
- 🚀 **Fast and Lightweight**: Minimal dependencies, fast analysis
- 🔄 **Git Integration**: Works seamlessly with Git repositories

## Installation

### Using pip

```bash
pip install weekly
```

### Using Poetry (recommended)

```bash
poetry add weekly
```

### For Development

```bash
# Clone the repository
git clone https://github.com/wronai/weekly.git
cd weekly

# Install with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

## Usage

### Basic Usage

Analyze a Python project:

```bash
weekly analyze /path/to/your/project
```

### Command Line Options

```
Usage: weekly analyze [OPTIONS] PROJECT_PATH

  Analyze a Python project and provide quality insights.

  PROJECT_PATH: Path to the project directory (default: current directory)

Options:
  -f, --format [text|json|markdown]  Output format (default: text)
  -o, --output FILE                  Output file (default: stdout)
  --show-suggestions / --no-suggestions
                                      Show improvement suggestions (default: true)
  -v, --verbose                      Show detailed output
  --help                             Show this message and exit.
```

### Examples

1. Analyze current directory and show results in the terminal:
   ```bash
   weekly analyze .
   ```

2. Generate a Markdown report:
   ```bash
   weekly analyze -f markdown -o report.md /path/to/project
   ```

3. Generate a JSON report for programmatic use:
   ```bash
   weekly analyze -f json -o report.json /path/to/project
   ```

## Output Example

### Text Output

```
📊 Weekly Project Analysis Report
================================================================================
Project: example-project
Generated: 2025-06-07 12:34:56

Summary:
--------------------------------------------------------------------------------
✅ 5 passed
⚠️  3 warnings
❌ 1 errors

Detailed Results:
--------------------------------------------------------------------------------
✅ Project Structure
  Found Python project with proper structure

✅ Dependencies
  All dependencies are properly specified
  
⚠️  Test Coverage
  Test coverage is below 80% (currently 65%)
  
  Suggestions:
    • Add more test cases to improve coverage
    • Consider using pytest-cov for coverage reporting

❌ Documentation
  Missing API documentation
  
  Suggestions:
    • Add docstrings to all public functions and classes
    • Consider using Sphinx or MkDocs for API documentation

Recommended Actions:
--------------------------------------------------------------------------------
1. Improve Test Coverage
   • Add unit tests for untested modules
   • Add integration tests for critical paths
   • Set up code coverage reporting in CI

2. Enhance Documentation
   • Add docstrings to all public APIs
   • Create API documentation using Sphinx or MkDocs
   • Add examples to the README
```

### Programmatic Usage

```python
from pathlib import Path
from weekly import analyze_project
from weekly.core.report import Report

# Analyze a project
report = analyze_project(Path("/path/to/your/project"))

# Get report as dictionary
report_data = report.to_dict()

# Get markdown report
markdown = report.to_markdown()

# Print summary
print(f"✅ {report.summary['success']} passed")
print(f"⚠️  {report.summary['warnings']} warnings")
print(f"❌ {report.summary['errors']} errors")

# Get suggestions
for suggestion in report.get_suggestions():
    print(f"\n{suggestion['title']}:")
    for item in suggestion['suggestions']:
        print(f"  • {item}")

### Most Active Files

- `src/main.py`: 12 changes
- `tests/test_main.py`: 8 changes
- `README.md`: 5 changes

### Languages Used

- `.py`: 15 files
- `.md`: 3 files
- `.json`: 2 files

## 📋 Next Steps

- [ ] Add tests for recent changes
- [ ] Refactor large files: src/utils.py, src/processor.py...

## 📜 Recent Commits

- `a1b2c3d` Fix bug in data processing (2023-05-15)
- `f4e5d6a` Add new feature X (2023-05-14)
- `b3c4d5e` Update documentation (2023-05-13)
- `c6d7e8f` Refactor module Y (2023-05-12)
- `d9e0f1a` Initial commit (2023-05-10)

*[View full history in the JSON file]*
```

## Development

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/wronai/weekly.git
   cd weekly
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```

### Running Tests

```bash
pytest
```

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run all checks:

```bash
black .
isort .
flake8
mypy .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ by the WronAI team
- Inspired by various Git analysis tools
