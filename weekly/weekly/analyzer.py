"""
Repository analyzer module for RepoFacts.
"""

import os
import json
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from collections import Counter

@dataclass
class CommitStats:
    """Class representing commit statistics."""
    hash: str
    author: str
    date: str
    message: str
    changes: List[Dict[str, str]] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

@dataclass
class RepoStatus:
    """Class representing repository status and statistics."""
    name: str
    description: str
    created_at: str
    last_commit: str
    total_commits: int
    contributors: Dict[str, int]
    file_changes: Dict[str, int]
    languages: Dict[str, int]
    commits: List[Dict[str, Any]]
    todos: List[str]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

class GitAnalyzer:
    """Class for analyzing Git repositories."""
    
    def __init__(self, repo_path: Path):
        """Initialize with repository path."""
        self.repo_path = repo_path
        self.now = datetime.now()
    
    def get_commit_history(self) -> List[CommitStats]:
        """Get complete commit history for the repository."""
        try:
            cmd = [
                'git', '-C', str(self.repo_path),
                'log',
                '--pretty=format:{"hash":"%H","author":"%an","date":"%ad","message":"%s"}',
                '--date=iso-strict',
                '--numstat',
                '--no-merges'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return self._parse_git_log(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit history for {self.repo_path.name}: {e}")
            return []
    
    def _parse_git_log(self, log_output: str) -> List[CommitStats]:
        """Parse git log output into structured data."""
        commits = []
        current_commit = None
        
        for line in log_output.strip().split('\n'):
            line = line.strip()
            if line.startswith('{'):
                if current_commit:
                    commits.append(current_commit)
                try:
                    data = json.loads(line)
                    current_commit = CommitStats(
                        hash=data['hash'],
                        author=data['author'],
                        date=data['date'],
                        message=data['message']
                    )
                except json.JSONDecodeError:
                    current_commit = None
            elif line and current_commit and '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    change = {
                        'additions': parts[0],
                        'deletions': parts[1],
                        'file': parts[2]
                    }
                    current_commit.changes.append(change)
                    
                    # Update totals
                    try:
                        current_commit.additions += int(parts[0]) if parts[0] != '-' else 0
                        current_commit.deletions += int(parts[1]) if parts[1] != '-' else 0
                    except ValueError:
                        pass
        
        if current_commit:
            commits.append(current_commit)
        
        return commits
    
    def get_repo_info(self) -> Dict[str, Any]:
        """Get repository information."""
        # Get first commit date as creation date
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'log', '--reverse', '--pretty=format:%ad', '--date=iso-strict'],
                capture_output=True, text=True, check=True
            )
            first_commit_date = result.stdout.split('\n')[0] if result.stdout else datetime.now().isoformat()
        except subprocess.CalledProcessError:
            first_commit_date = datetime.now().isoformat()
            
        return {
            'created_at': first_commit_date,
            'description': self._get_readme_content()
        }
    
    def _get_readme_content(self) -> str:
        """Extract first line from README as description."""
        readme = next((f for f in self.repo_path.glob('README*')), None)
        if readme and readme.is_file():
            try:
                with open(readme, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    return first_line if first_line and not first_line.startswith('#') else 'No description'
            except Exception:
                pass
        return 'No description'
    
    def analyze(self) -> Optional[RepoStatus]:
        """Analyze repository and return complete status."""
        print(f"Analyzing {self.repo_path.name}...")
        
        # Get repository info
        repo_info = self.get_repo_info()
        
        # Get complete commit history
        commits = self.get_commit_history()
        if not commits:
            return None
        
        # Calculate statistics
        author_counts = Counter()
        file_changes = Counter()
        languages = Counter()
        
        for commit in commits:
            author_counts[commit.author] += 1
            for change in commit.changes:
                file_path = change['file']
                file_changes[file_path] += 1
                
                # Get file extension
                ext = os.path.splitext(file_path)[1].lower()
                if ext:
                    languages[ext] += 1
        
        # Generate TODOs
        todos = self._generate_todos(commits, file_changes)
        
        # Prepare commits for JSON serialization
        serialized_commits = [commit.to_dict() for commit in commits]
        
        return RepoStatus(
            name=self.repo_path.name,
            description=repo_info['description'],
            created_at=repo_info['created_at'],
            last_commit=commits[0].date if commits else '',
            total_commits=len(commits),
            contributors=dict(author_counts.most_common(10)),
            file_changes=dict(file_changes.most_common(10)),
            languages=dict(languages.most_common(5)),
            commits=serialized_commits,
            todos=todos
        )
    
    def _generate_todos(self, commits: List[CommitStats], file_changes: Dict) -> List[str]:
        """Generate TODO items based on repository analysis."""
        todos = []
        
        # Check for recent activity without tests
        recent_commits = commits[:10]
        has_code_changes = any(
            any(not change['file'].endswith(('.md', '.txt')) for change in commit.changes)
            for commit in recent_commits
        )
        has_test_changes = any(
            'test' in change['file'].lower()
            for commit in recent_commits
            for change in commit.changes
        )
        
        if has_code_changes and not has_test_changes:
            todos.append("Add tests for recent changes")
        
        # Check for large files that might need splitting
        large_files = [f for f, count in file_changes.items() 
                      if count > 50 and any(f.endswith(ext) for ext in ['.py', '.js', '.ts', '.go'])]
        if large_files:
            todos.append(f"Refactor large files: {', '.join(large_files[:2])}...")
        
        return todos or ["No critical issues found"]
