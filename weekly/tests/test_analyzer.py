"""Tests for the analyzer module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from weekly.core.repo_status import RepoStatus
from weekly.git_scanner import GitRepo, ScanResult
from weekly import GitAnalyzer, CommitStats
from datetime import datetime, timedelta
from pathlib import Path

def test_commit_stats_initialization():
    """Test CommitStats initialization and to_dict method."""
    commit = CommitStats(
        hash="a1b2c3d",
        author="test@example.com",
        date="2023-01-01T12:00:00Z",
        message="Initial commit",
        changes=[{"file": "README.md", "additions": "10", "deletions": "0"}],
        additions=10,
        deletions=0
    )
    
    assert commit.hash == "a1b2c3d"
    assert commit.to_dict()["hash"] == "a1b2c3d"

def test_repo_status_initialization():
    """Test RepoStatus initialization and to_dict method."""
    status = RepoStatus(
        name="test-repo",
        description="Test repository",
        created_at="2023-01-01T00:00:00Z",
        last_commit="2023-05-01T12:00:00Z",
        total_commits=42,
        contributors={"user1": 30, "user2": 12},
        file_changes={"file1.txt": 10, "file2.txt": 5},
        languages={".py": 5, ".md": 2},
        commits=[],
        todos=["Add tests"]
    )
    
    assert status.name == "test-repo"
    assert status.total_commits == 42
    assert status.to_dict()["name"] == "test-repo"

@patch('subprocess.run')
def test_git_analyzer_get_commit_history(mock_run):
    """Test GitAnalyzer commit history parsing."""
    # Mock git log output
    mock_output = """
{"hash":"a1b2c3d","author":"test","date":"2023-01-01T12:00:00Z","message":"Initial commit"}
10\t5\tfile1.txt
-\t-\tfile2.txt
    """.strip()
    
    # Configure mock
    mock_result = MagicMock()
    mock_result.stdout = mock_output
    mock_run.return_value = mock_result
    
    # Test
    analyzer = GitAnalyzer(Path("/fake/repo"))
    commits = analyzer.get_commit_history()
    
    # Assertions
    assert len(commits) == 1
    assert commits[0].hash == "a1b2c3d"
    assert len(commits[0].changes) == 2
    # The test data has 10 additions and 5 deletions in the changes
    # but our implementation sums them up in the analyze() method, not here

@patch('subprocess.run')
def test_git_analyzer_analyze(mock_run):
    """Test GitAnalyzer analyze method."""
    # Mock git log output
    mock_log = """
{"hash":"a1b2c3d","author":"test","date":"2023-01-01T12:00:00Z","message":"Initial commit"}
10\t5\tsrc/main.py
-\t-\ttests/test_main.py
    """.strip()
    
    # Mock git log --reverse output
    mock_log_reverse = "2023-01-01T12:00:00Z"
    
    # Configure mock
    mock_result = MagicMock()
    mock_result.stdout = mock_log
    mock_result_reverse = MagicMock()
    mock_result_reverse.stdout = mock_log_reverse
    
    # Make run return different values based on arguments
    def run_side_effect(*args, **kwargs):
        if '--reverse' in args[0]:
            return mock_result_reverse
        return mock_result
    
    mock_run.side_effect = run_side_effect
    
    # Test
    analyzer = GitAnalyzer(Path("/fake/repo"))
    status = analyzer.analyze()
    
    # Assertions
    assert status is not None
    assert status.name == "repo"  # The repo name from the test path
    assert status.total_commits == 1
    # The test data has one commit from 'test' author
    assert status.contributors == {"test": 1}
    # The test data includes a .py file
    assert ".py" in status.languages
    # Our implementation always includes some TODOs
    assert len(status.todos) > 0
