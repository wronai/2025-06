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

@patch('weekly.cli.analyze_project')
def test_analyze_command(mock_analyze, runner, tmp_path):
    """Test the analyze command."""
    # Setup mock
    mock_report = MagicMock()
    mock_report.to_dict.return_value = {"name": "test-repo"}
    mock_analyze.return_value = mock_report
    
    # Create a temporary directory with a Python file
    project_path = tmp_path / "test-project"
    project_path.mkdir()
    (project_path / "test.py").write_text("def hello(): pass\n")
    
    # Run the command
    output_file = tmp_path / "output.json"
    result = runner.invoke(main, ["analyze", str(project_path), "--output", str(output_file)])
    
    # Check results
    assert result.exit_code == 0
    assert "Analyzing project at" in result.output
    assert output_file.exists()

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
    assert "Weekly - Analyze your Python project's quality and get suggestions for improvement." in result.output
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

@patch('weekly.git_scanner.GitScanner.scan_directory')
def test_analyze_org_command_no_repos(mock_scan, runner, tmp_path):
    """Test the scan command with a directory containing no Git repos."""
    # Setup mock to return no repositories
    mock_scan.return_value = []
    
    # Create an empty directory
    empty_dir = tmp_path / "empty-org"
    empty_dir.mkdir()
    
    # Run the command
    result = runner.invoke(main, ["scan", str(empty_dir)])
    
    # Check results
    assert result.exit_code == 0  # Should exit with success even if no repos found
    assert "No Git repositories found" in result.output
