"""Tests for the reporter module."""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from weekly.core.repo_status import RepoStatus
from weekly.reporter import ReportGenerator

@pytest.fixture
def sample_status():
    """Create a sample RepoStatus instance for testing."""
    return RepoStatus(
        name="test-repo",
        description="A test repository",
        created_at="2023-01-01T00:00:00Z",
        last_commit="2023-05-15T10:30:00Z",
        total_commits=42,
        contributors={"user1": 30, "user2": 12},
        file_changes={"src/main.py": 15, "README.md": 5, "tests/test_main.py": 8},
        languages={".py": 10, ".md": 2},
        commits=[
            {
                "hash": "a1b2c3d",
                "author": "user1",
                "date": "2023-05-15T10:30:00Z",
                "message": "Fix bug in main function",
                "changes": [{"file": "src/main.py", "additions": "5", "deletions": "2"}],
                "additions": 5,
                "deletions": 2
            },
            {
                "hash": "b2c3d4e",
                "author": "user2",
                "date": "2023-05-10T14:20:00Z",
                "message": "Initial commit",
                "changes": [
                    {"file": "src/main.py", "additions": "10", "deletions": "0"},
                    {"file": "README.md", "additions": "5", "deletions": "0"}
                ],
                "additions": 15,
                "deletions": 0
            }
        ],
        todos=["Add more tests", "Update documentation"]
    )

def test_generate_markdown(sample_status):
    """Test markdown report generation."""
    # Generate markdown
    markdown_content = ReportGenerator.generate_markdown(sample_status)
    
    # Check basic structure
    assert f"# {sample_status.name}" in markdown_content
    assert f"**{sample_status.description}**" in markdown_content
    assert "## 📊 Project Overview" in markdown_content
    assert "## 📋 Next Steps" in markdown_content
    
    # Check some dynamic content
    assert str(sample_status.total_commits) in markdown_content
    assert "user1: 30 commits" in markdown_content
    assert "`src/main.py`: 15 changes" in markdown_content
    assert "- [ ] Add more tests" in markdown_content

def test_generate_html(sample_status):
    """Test HTML report generation."""
    # Generate markdown first
    markdown_content = ReportGenerator.generate_markdown(sample_status)
    
    # Generate HTML
    html_content = ReportGenerator.generate_html(sample_status, markdown_content)
    
    # Check basic structure
    assert "<!DOCTYPE html>" in html_content
    assert f"<title>{sample_status.name}" in html_content
    assert "<h1>test-repo</h1>" in html_content
    assert "Download Markdown" in html_content
    
    # Check some dynamic content
    assert str(sample_status.total_commits) in html_content
    assert "user1: 30 commits" in html_content

@patch('builtins.open', new_callable=MagicMock)
@patch('json.dump')
def test_save_reports(mock_json_dump, mock_open, sample_status, tmp_path):
    """Test saving all report files."""
    # Create a temporary directory
    output_dir = tmp_path / "reports" / "test-repo"
    
    # Save reports
    ReportGenerator.save_reports(sample_status, output_dir)
    
    # Check if output directory was created
    assert output_dir.exists()
    
    # Check if all files were created
    expected_files = ["status.json", "status.md", "index.html"]
    for filename in expected_files:
        assert (output_dir / filename).exists()
    
    # Check if json.dump was called with the status data
    args, _ = mock_json_dump.call_args
    assert args[0]["name"] == sample_status.name
    assert args[0]["total_commits"] == sample_status.total_commits
