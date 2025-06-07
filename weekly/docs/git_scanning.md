# Git Repository Scanning with Weekly

Weekly provides powerful tools for scanning multiple Git repositories in a directory structure, generating comprehensive reports for each repository, and creating a summary report with links to all individual reports.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Scanning Multiple Repositories](#scanning-multiple-repositories)
- [Date-Based Filtering](#date-based-filtering)
- [Output Options](#output-options)
- [Examples](#examples)
  - [Basic Scan](#basic-scan)
  - [Date-Based Filtering](#date-based-filtering)
  - [Custom Output Directory](#custom-output-directory)
  - [Generate JSON Reports](#generate-json-reports)
  - [Programmatic Usage](#programmatic-usage)

## Basic Usage

The simplest way to scan Git repositories is to use the `weekly scan` command:

```bash
weekly scan /path/to/repositories
```

This will:
1. Recursively scan the specified directory for Git repositories
2. Run all available checkers on each repository
3. Generate an HTML report for each repository in the `./weekly-reports` directory
4. Create a summary HTML report with links to all individual reports

## Scanning Multiple Repositories

Weekly is designed to work with the common directory structure where repositories are organized by organization and repository name:

```
github/
  organization1/
    repo1/
    repo2/
  organization2/
    repo1/
    repo2/
```

When you run the scanner on the `github` directory, it will:
1. Find all Git repositories in the directory structure
2. Extract the organization and repository names from the directory structure
3. Generate individual reports for each repository
4. Create a summary report with links to all repositories

## Date-Based Filtering

You can filter repositories based on when they were last modified using the `--since` flag:

```bash
# Only include repositories with changes in the last 7 days (default)
weekly scan /path/to/repositories --since "7 days ago"

# Only include repositories with changes since a specific date
weekly scan /path/to/repositories --since "2023-01-01"

# Only include repositories with changes in the last 30 days
weekly scan /path/to/repositories --since "30 days ago"
```

## Output Options

### Output Directory

By default, reports are saved in the `./weekly-reports` directory. You can specify a custom output directory:

```bash
weekly scan /path/to/repositories -o ./my-reports
```

### Report Format

Weekly supports multiple output formats:

```bash
# HTML (default)
weekly scan /path/to/repositories -f html

# JSON
weekly scan /path/to/repositories -f json

# Markdown
weekly scan /path/to/repositories -f markdown
```

### Summary-Only Mode

If you only want the summary report and not individual reports for each repository:

```bash
weekly scan /path/to/repositories --summary-only
```

## Examples

### Basic Scan

Scan all repositories in the `~/github` directory:

```bash
weekly scan ~/github
```

### Date-Based Filtering

Scan only repositories with changes in the last 14 days:

```bash
weekly scan ~/github --since "14 days ago"
```

### Custom Output Directory

Save reports to a custom directory:

```bash
weekly scan ~/github -o ~/weekly-reports
```

### Generate JSON Reports

Generate JSON reports instead of HTML:

```bash
weekly scan ~/github -f json -o ./json-reports
```

### Programmatic Usage

You can also use the Git scanner programmatically:

```python
from pathlib import Path
from datetime import datetime, timedelta
from weekly import GitScanner

# Create a scanner instance
scanner = GitScanner(
    root_dir=Path.home() / "github",  # Directory containing your Git repositories
    output_dir="weekly-reports",      # Output directory for reports
    since=datetime.now() - timedelta(days=7),  # Only include recent changes
    recursive=True,                   # Scan subdirectories
    jobs=4                           # Number of parallel jobs
)

# Run the scan
results = scanner.scan_all()

# Process results
print(f"Scanned {len(results)} repositories")
for result in results:
    status = "✅" if not result.error and all(r.is_ok for r in result.results.values()) else "❌"
    print(f"{status} {result.repo.org}/{result.repo.name}")
    if result.error:
        print(f"   Error: {result.error}")
    for name, check in result.results.items():
        status = "✓" if check.is_ok else "✗"
        print(f"   {status} {name}: {check.message}")
```

## Report Structure

When you run the scanner, it creates the following directory structure:

```
output-dir/
  summary.html                 # Summary report with links to all repositories
  organization1/
    repo1/
      latest.html -> report_20230607_143022.html  # Symlink to latest report
      report_20230607_143022.html  # Individual report with timestamp
    repo2/
      latest.html -> report_20230607_143022.html
      report_20230607_143022.html
  organization2/
    repo1/
      latest.html -> report_20230607_143022.html
      report_20230607_143022.html
```

The summary report includes:
- List of all scanned repositories
- Status of each repository (pass/fail)
- Last commit date
- Links to individual reports
- Summary statistics

## Tips for Large Repositories

For large repositories or many repositories, you can:

1. Increase the number of parallel jobs:
   ```bash
   weekly scan /path/to/repositories -j 8
   ```

2. Use date-based filtering to only scan active repositories:
   ```bash
   weekly scan /path/to/repositories --since "30 days ago"
   ```

3. Generate reports in JSON format for further processing:
   ```bash
   weekly scan /path/to/repositories -f json -o ./reports
   ```

4. Use the `--summary-only` flag if you only need the summary report:
   ```bash
   weekly scan /path/to/repositories --summary-only
   ```

## Troubleshooting

### No repositories found

If no repositories are found, check:

1. The directory path is correct
2. The directory contains Git repositories
3. You have read permissions for the directory

### Permission denied errors

If you get permission errors, try running the command with `sudo` or ensure the current user has the necessary permissions:

```bash
sudo weekly scan /path/to/repositories
# or
chmod -R +r /path/to/repositories
```

### Report generation errors

If you encounter errors during report generation, try:

1. Updating to the latest version of Weekly
2. Checking the error message for more details
3. Running with the `-v` flag for verbose output:
   ```bash
   weekly scan /path/to/repositories -v
   ```

## Conclusion

The Weekly Git scanner provides a powerful way to analyze multiple Git repositories at once, with support for filtering by date, generating different report formats, and running checks in parallel. Whether you're managing a handful of repositories or hundreds, Weekly can help you keep track of code quality across your entire organization.
