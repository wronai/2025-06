# Weekly Examples

This directory contains example scripts demonstrating how to use the Weekly package.

## Git Scanner Example

The `git_scan_example.py` script shows how to use the `GitScanner` class to scan multiple Git repositories and generate quality reports.

### Prerequisites

- Python 3.7+
- Git installed and in your PATH
- Weekly package installed in development mode or in your Python environment

### Running the Example

1. Make sure you have some Git repositories in the directory you want to scan (default is `~/github`)
2. Run the script:

```bash
python examples/git_scan_example.py
```

### Customizing the Scan

You can modify the following variables in the script to customize the scan:

- `root_dir`: Directory containing your Git repositories (default: `~/github`)
- `output_dir`: Where to save the generated reports (default: `weekly-reports`)
- `since_days`: Only include repositories with changes in the last X days (default: 7)
- `recursive`: Whether to scan subdirectories recursively (default: `True`)
- `jobs`: Number of parallel jobs to use (default: 4)

### Output

The script will:
1. Scan all Git repositories in the specified directory
2. Run quality checks on each repository
3. Generate individual HTML reports in the output directory
4. Create a summary HTML report with links to all individual reports

### Example Output

```
🔍 Scanning Git repositories in /Users/username/github...

✅ Scan complete! Generated reports for 3 repositories.
📊 Summary report: weekly-reports/summary.html

✅ org1/repo1: 5 checks
   ✓ style: Passed
   ✓ code_quality: Passed
   ✓ dependencies: 2 outdated packages found
   ✓ docs: Documentation is 85% complete
   ✓ tests: 92% test coverage

✅ org2/repo2: 5 checks
   ✗ style: 3 formatting issues found
   ✓ code_quality: Passed
   ✓ dependencies: All dependencies are up to date
   ✓ docs: Documentation is 92% complete
   ✓ tests: 95% test coverage
```

### Viewing Reports

Open the generated HTML files in your web browser to view the detailed reports. The summary report (`summary.html`) provides an overview of all scanned repositories with links to individual reports.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](../LICENSE) file for details.
