"""Tests for the CLI module."""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from weekly.cli import main
from weekly.core.repo_status import RepoStatus

@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()

def test_analyze_command(runner, tmp_path):
    """Test the analyze command with a simple project."""
    # Create a minimal Python project
    project_path = tmp_path / "test-project"
    project_path.mkdir()
    
    # Create a simple Python file
    (project_path / "test.py").write_text("""def hello():
    print(\"Hello, World!\")""")
    
    # Create a simple pyproject.toml to make it a valid project
    (project_path / "pyproject.toml").write_text("""
    [build-system]
    requires = ["setuptools>=42"]
    build-backend = "setuptools.build_meta"
    
    [project]
    name = "test-project"
    version = "0.1.0"
    """)
    
    # Run the analyze command
    result = runner.invoke(main, ["analyze", str(project_path)])
    
    # Check that the command ran successfully
    assert result.exit_code == 0
    assert "Analyzing project at" in result.output

@patch('weekly.git_scanner.GitScanner.find_git_repos')
def test_analyze_org_command(mock_find, runner, tmp_path):
    """Test the scan command for multiple repositories."""
    # Setup mock
    mock_repo = MagicMock()
    mock_repo.path = tmp_path / "org" / "test-repo"
    mock_repo.path.mkdir(parents=True)
    mock_find.return_value = [mock_repo]
    
    # Create output directory
    output_dir = tmp_path / "output"
    
    # Run the command
    result = runner.invoke(main, ["scan", str(tmp_path / "org"), "--output-dir", str(output_dir)])
    
    # Check results
    assert result.exit_code == 0
    assert "Scanning directory" in result.output

def test_cli_help(runner):
    """Test the CLI help output."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    # Check for key parts of the help text without being too strict about formatting
    assert "Weekly" in result.output
    assert "Analyze your Python project's quality" in result.output
    assert "analyze" in result.output
    assert "scan" in result.output

@patch('weekly.git_analyzer.GitAnalyzer')
def test_analyze_command_no_repo(mock_analyzer, runner, tmp_path):
    """Test the analyze command with a non-existent repository."""
    # Setup mock to return None (no repo found)
    mock_analyzer.return_value.analyze.return_value = None
    
    # Run the command with a non-existent path
    non_existent_path = tmp_path / "nonexistent"
    result = runner.invoke(main, ["analyze", str(non_existent_path)])
    
    # Check results
    assert result.exit_code != 0
    assert "does not exist" in result.output

@patch('weekly.git_scanner.GitScanner.find_git_repos')
def test_analyze_org_command_no_repos(mock_find, runner, tmp_path):
    """Test the scan command with a directory containing no Git repos."""
    # Setup mock to return no repositories
    mock_find.return_value = []
    
    # Create an empty directory
    empty_dir = tmp_path / "empty-org"
    empty_dir.mkdir()
    
    # Run the command
    result = runner.invoke(main, ["scan", str(empty_dir)])
    
    # Check results
    assert result.exit_code == 0  # Should exit with success even if no repos found
    assert "No Git repositories found" in result.output
