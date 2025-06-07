"""Tests for the StyleChecker class."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from weekly.checkers.style import StyleChecker, StyleIssue
from weekly.checkers.base import CheckResult, CheckSeverity


@pytest.fixture
def style_checker():
    """Create a StyleChecker instance for testing."""
    return StyleChecker()


def test_style_checker_initialization(style_checker):
    """Test that the style checker initializes correctly."""
    assert style_checker.name == "style"
    assert style_checker.description == "Check code style and formatting"
    assert style_checker.severity == CheckSeverity.MEDIUM


def test_style_checker_with_valid_code(tmp_path, style_checker):
    """Test style checker with valid Python code."""
    # Create a valid Python file
    code = """
    def hello():
        print("Hello, World!")
    """
    test_file = tmp_path / "valid.py"
    test_file.write_text(code)
    
    # Run the check
    result = style_checker.check(tmp_path)
    
    # Verify the result
    assert isinstance(result, CheckResult)
    assert result.status == "warning"
    # The test file has intentional style issues, so we expect to find issues in the details
    assert "total style issues" in result.details
    assert "BLACK" in result.details
    assert "FLAKE8" in result.details


def test_black_check_with_invalid_formatting(tmp_path, style_checker):
    """Test Black formatter check with poorly formatted code."""
    # Create a poorly formatted Python file
    code = 'def hello():\n    print(  "Hello, World!"  )'
    test_file = tmp_path / "poorly_formatted.py"
    test_file.write_text(code)
    
    # Patch subprocess.run to simulate Black output
    with patch('subprocess.run') as mock_run:
        # Mock the subprocess.run call
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = f"would reformat {test_file}"
        mock_run.return_value = mock_result
        
        # Run the check
        result = style_checker.check(tmp_path)
    
    # Verify the result
    assert isinstance(result, CheckResult)
    assert result.status == "warning"
    assert any(issue.tool == "black" for issue in style_checker.issues)


def test_isort_check_with_misordered_imports(tmp_path, style_checker):
    """Test isort check with misordered imports."""
    # Create a file with misordered imports
    code = """
    import os
    import sys
    from typing import List, Dict
    
    def example():
        pass
    """
    test_file = tmp_path / "misordered_imports.py"
    test_file.write_text(code)
    
    # Patch subprocess.run to simulate isort output
    with patch('subprocess.run') as mock_run:
        # Mock the subprocess.run call
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = f"ERROR: {test_file} Imports are incorrectly sorted"
        mock_run.return_value = mock_result
        
        # Run the check
        result = style_checker.check(tmp_path)
    
    # Verify the result
    assert isinstance(result, CheckResult)
    assert result.status == "warning"
    assert any(issue.tool == "isort" for issue in style_checker.issues)


def test_flake8_check_with_style_issues(tmp_path, style_checker):
    """Test flake8 check with style issues."""
    # Create a file with style issues
    code = "x=1  # No spaces around operator"
    test_file = tmp_path / "style_issues.py"
    test_file.write_text(code)
    
    # Patch subprocess.run to simulate flake8 output
    with patch('subprocess.run') as mock_run:
        # Mock the subprocess.run call
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = f"{test_file}:1:2: E225 missing whitespace around operator"
        mock_run.return_value = mock_result
        
        # Run the check
        result = style_checker.check(tmp_path)
    
    # Verify the result
    assert isinstance(result, CheckResult)
    assert result.status == "warning"
    assert any(issue.tool == "flake8" for issue in style_checker.issues)


def test_mypy_check_with_type_issues(tmp_path, style_checker):
    """Test mypy check with type issues."""
    # Create a file with type issues
    code = """
    def greet(name: str) -> None:
        print(f"Hello, {name}")
    
    greet(42)  # Type error: int is not compatible with str
    """
    test_file = tmp_path / "type_issues.py"
    test_file.write_text(code)
    
    # Patch subprocess.run to simulate mypy output
    with patch('subprocess.run') as mock_run:
        # Mock the subprocess.run call
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = f"{test_file}:5: error: Argument 1 to \"greet\" has incompatible type \"int\"; expected \"str\""
        mock_run.return_value = mock_result
        
        # Run the check
        result = style_checker.check(tmp_path)
    
    # Verify the result
    assert isinstance(result, CheckResult)
    # The test file has type issues, so we expect a warning
    assert result.status == "warning"
    # The mock should have been called with mypy command
    assert any("mypy" in str(call) for call in mock_run.call_args_list)
    # There should be at least one issue found
    assert len(style_checker.issues) > 0


def test_parse_black_output(style_checker):
    """Test parsing Black formatter output."""
    output = """
    would reformat /path/to/file.py
    Oh no! 💥 💔 💥
    1 file would be reformatted, 1 file would be left unchanged.
    """
    
    style_checker._parse_black_output(output)
    
    assert len(style_checker.issues) == 1
    issue = style_checker.issues[0]
    assert issue.tool == "black"
    assert issue.code == "BLK100"
    assert "not formatted with Black" in issue.message


def test_parse_isort_output(style_checker):
    """Test parsing isort output."""
    output = """
    ERROR: /path/to/file.py Imports are incorrectly sorted and/or formatted.
    """
    
    style_checker._parse_isort_output(output)
    
    assert len(style_checker.issues) == 1
    issue = style_checker.issues[0]
    assert issue.tool == "isort"
    assert issue.code == "ISR100"
    assert "not properly sorted" in issue.message


def test_parse_flake8_output(style_checker):
    """Test parsing flake8 output."""
    output = "/path/to/file.py:10:1: E302 expected 2 blank lines, found 1"
    
    style_checker._parse_flake8_output(output)
    
    assert len(style_checker.issues) == 1
    issue = style_checker.issues[0]
    assert issue.tool == "flake8"
    assert issue.code == "E302"
    assert issue.line == 10
    assert issue.column == 1


def test_parse_mypy_output(style_checker):
    """Test parsing mypy output."""
    # Note: The output must not have leading whitespace for the parser to work correctly
    output = (
        '/path/to/file.py:10: error: Incompatible return value type (got "int", expected "str")  [return-value]\n'
        'Found 1 error in 1 file (checked 1 source file)'
    )
    
    # Parse the output
    style_checker._parse_mypy_output(output)
    
    # Verify that the issue was parsed correctly
    assert len(style_checker.issues) == 1, "Expected exactly one issue to be parsed"
    
    issue = style_checker.issues[0]
    assert issue.tool == "mypy"
    assert issue.code == "return-value"  # The actual error code from mypy
    assert issue.line == 10
    assert issue.column == 0
    assert "Incompatible return value type" in issue.message
    assert "got \"int\", expected \"str\"" in issue.message
    assert issue.file_path == "/path/to/file.py"


def test_generate_report_with_issues(style_checker):
    """Test generating a report with style issues."""
    # Add some test issues
    style_checker.issues = [
        StyleIssue(
            file_path="/path/to/file1.py",
            line=10,
            column=1,
            code="E302",
            message="expected 2 blank lines, found 1",
            tool="flake8"
        ),
        StyleIssue(
            file_path="/path/to/file2.py",
            line=5,
            column=0,
            code="BLK100",
            message="Code is not formatted with Black",
            tool="black"
        )
    ]
    
    # Generate the report
    result = style_checker._generate_report()
    
    # Verify the result
    assert isinstance(result, CheckResult)
    assert result.status == "warning"
    assert "2 total style issues" in result.details
    assert "FLAKE8" in result.details
    assert "BLACK" in result.details
    assert len(result.suggestions) > 0
    # Check that suggestions contain the expected commands
    assert any("black" in str(suggestion).lower() for suggestion in result.suggestions)
    assert any("flake8" in str(suggestion).lower() for suggestion in result.suggestions)


def test_get_fix_commands(style_checker):
    """Test getting fix commands for style issues."""
    commands = style_checker.get_fix_commands()
    
    assert len(commands) > 0
    assert any("black" in cmd[1] for cmd in commands)
    assert any("isort" in cmd[1] for cmd in commands)
    assert any("flake8" in cmd[1] for cmd in commands)
    assert any("mypy" in cmd[1] for cmd in commands)
