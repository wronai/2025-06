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

@patch('weekly.git_analyzer.GitAnalyzer')
def test_analyze_command(mock_analyzer, runner, tmp_path):
    """Test the analyze command."""
    # Setup mock
    mock_status = MagicMock(spec=RepoStatus)
    mock_status.name = "test-repo"
    mock_status.to_dict.return_value = {"name": "test-repo"}
    mock_analyzer.return_value.analyze.return_value = mock_status
    
    # Create a temporary repository directory
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()  # Make it look like a git repo
    
    # Run the command
    result = runner.invoke(main, ["analyze", str(repo_path), "--output", str(tmp_path / "output")])
    
    # Check results
    assert result.exit_code == 0
    assert "Generated reports for test-repo" in result.output
    assert (tmp_path / "output" / "test-repo").exists()

@patch('weekly.git_analyzer.GitAnalyzer')
def test_analyze_org_command(mock_analyzer, runner, tmp_path):
    """Test the analyze-org command."""
    # Setup mock
    mock_status = MagicMock(spec=RepoStatus)
    mock_status.name = "test-repo"
    mock_status.to_dict.return_value = {"name": "test-repo"}
    mock_analyzer.return_value.analyze.return_value = mock_status
    
    # Create a temporary organization directory with a repo
    org_path = tmp_path / "org"
    repo_path = org_path / "test-repo"
    repo_path.mkdir(parents=True)
    (repo_path / ".git").mkdir()  # Make it look like a git repo
    
    # Run the command
    result = runner.invoke(main, ["scan", str(org_path), "--output-dir", str(tmp_path / "output")])
    
    # Check results
    assert result.exit_code == 0
    assert "Generated reports for test-repo" in result.output
    assert (tmp_path / "output" / "test-repo").exists()
    assert (tmp_path / "output" / "summary.json").exists()

def test_cli_help(runner):
    """Test the CLI help output."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Generate comprehensive reports from Git repositories" in result.output
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

@patch('weekly.git_analyzer.GitAnalyzer')
def test_analyze_org_command_no_repos(mock_analyzer, runner, tmp_path):
    """Test the analyze-org command with a directory containing no Git repos."""
    # Create an empty directory
    empty_dir = tmp_path / "empty-org"
    empty_dir.mkdir()
    
    # Run the command
    result = runner.invoke(main, ["scan", str(empty_dir)])
    
    # Check results
    assert result.exit_code != 0
    assert "No Git repositories found" in result.output
