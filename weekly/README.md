# RepoFacts

[![PyPI](https://img.shields.io/pypi/v/repofacts)](https://pypi.org/project/repofacts/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/repofacts.svg)](https://pypi.org/project/repofacts/)

RepoFacts is a powerful command-line tool for generating comprehensive reports from Git repositories. It analyzes repository history, contributors, file changes, and more, then generates beautiful HTML, Markdown, and JSON reports.

## Features

- 📊 **Complete Repository Analysis**: Get insights into commits, contributors, and file changes
- 📝 **Multiple Output Formats**: Generate reports in HTML, Markdown, and JSON
- 🔍 **Deep Git History**: Analyze complete commit history with detailed statistics
- 🎨 **Beautiful Reports**: Clean, responsive HTML reports with download options
- 🚀 **CLI Interface**: Easy-to-use command line interface
- 📦 **Python Package**: Integrate with your own Python projects

## Installation

```bash
pip install repofacts
```

For development:

```bash
git clone https://github.com/wronai/repofacts.git
cd repofacts
pip install -e .[dev]
```

## Usage

### Analyze a single repository

```bash
repofacts analyze /path/to/repo
```

### Analyze all repositories in a directory

```bash
repofacts analyze-org /path/to/organization/dir
```

### Options

```
Options:
  -o, --output PATH  Output directory for reports (default: ./reports)
  --help             Show this message and exit.
```

## Output Structure

For each repository, RepoFacts generates the following files:

```
reports/
└── repository-name/
    ├── status.json    # Complete repository data including full commit history
    ├── status.md       # Markdown report
    └── index.html      # HTML report with download option
```

## Example Reports

### HTML Report

![HTML Report](https://example.com/path/to/screenshot.png)  <!-- TODO: Add screenshot -->

### Markdown Report

```markdown
# repository-name

**Repository description**

## 📊 Project Overview

- **Created:** 2023-01-01
- **Last Updated:** 2023-05-15
- **Total Commits:** 42
- **Contributors:** 3

### Top Contributors

- Alice: 25 commits
- Bob: 15 commits
- Charlie: 2 commits

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
   git clone https://github.com/wronai/repofacts.git
   cd repofacts
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
