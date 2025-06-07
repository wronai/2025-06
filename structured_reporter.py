#!/usr/bin/env python3
"""
Structured WronAI Ecosystem Reporter

Generates reports in a structured format with complete history.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional
import markdown
from dataclasses import dataclass, asdict, field

# Configuration
BASE_DIR = Path('/home/tom/github/wronai')
REPORTS_DIR = BASE_DIR / '2025-06' / 'reports'
TEMPLATES_DIR = Path(__file__).parent / 'templates'

# Ensure directories exist
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

@dataclass
class CommitStats:
    hash: str
    author: str
    date: str
    message: str
    changes: List[Dict[str, str]] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0

@dataclass
class RepoStatus:
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

class GitAnalyzer:
    def __init__(self, repo_path: Path):
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
        serialized_commits = [asdict(commit) for commit in commits]
        
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

class ReportGenerator:
    @staticmethod
    def generate_markdown(status: RepoStatus) -> str:
        """Generate markdown report from status data."""
        return f"""# {status.name}

**{status.description}**

## 📊 Project Overview

- **Created:** {status.created_at[:10]}
- **Last Updated:** {status.last_commit[:10] if status.last_commit else 'N/A'}
- **Total Commits:** {status.total_commits}

### Top Contributors
{"\n".join(f"- {author}: {count} commits" for author, count in status.contributors.items())}

### Most Active Files
{"\n".join(f"- {file}: {count} changes" for file, count in status.file_changes.items())}

### Languages Used
{"\n".join(f"- {ext}: {count} files" for ext, count in status.languages.items())}

## 📋 Next Steps
{"\n".join(f"- [ ] {todo}" for todo in status.todos)}

## 📜 Recent Commits

{"\n".join(f"- `{c['hash'][:7]}` {c['message']} ({c['date'][:10]})" for c in status.commits[:5])}

*[View full history in the JSON file]*
"""

    @staticmethod
    def generate_html(status: RepoStatus, markdown_content: str) -> str:
        """Generate HTML report with download option."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{status.name} - WronAI Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        pre, code {{ 
            background: #f8f9fa;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        }}
        pre {{
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto;
            border-left: 3px solid #4e73df;
        }}
        code {{
            padding: 2px 5px; 
            border-radius: 3px; 
            font-size: 0.9em;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .download-btn {{
            background: #4e73df;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.9em;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 3px solid #4e73df;
        }}
        .metric-card h3 {{ margin: 0 0 10px 0; color: #4e73df; }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 0.9em;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{status.name}</h1>
        <a href="status.md" class="download-btn" download>Download Markdown</a>
    </div>
    
    <div class="content">
        {markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])}
    </div>
    
    <div class="footer">
        Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by WronAI Ecosystem Reporter
    </div>
</body>
</html>"""

def save_reports(repo_name: str, status: RepoStatus, reports_dir: Path):
    """Save all report files for a repository."""
    # Create repo directory
    repo_dir = reports_dir / repo_name
    repo_dir.mkdir(exist_ok=True)
    
    # Save status.json
    with open(repo_dir / 'status.json', 'w') as f:
        json.dump(asdict(status), f, indent=2, default=str)
    
    # Generate and save markdown
    md_content = ReportGenerator.generate_markdown(status)
    with open(repo_dir / 'status.md', 'w') as f:
        f.write(md_content)
    
    # Generate and save HTML
    html_content = ReportGenerator.generate_html(status, md_content)
    with open(repo_dir / 'index.html', 'w') as f:
        f.write(html_content)

def main():
    """Main function to generate reports for all repositories."""
    print("🚀 Starting WronAI Ecosystem Analysis")
    
    # Get all git repositories
    repos = [d for d in BASE_DIR.iterdir() 
             if d.is_dir() and (d / '.git').exists() and d.name != 'venv']
    
    all_repos_status = []
    
    for repo_path in repos:
        analyzer = GitAnalyzer(repo_path)
        status = analyzer.analyze()
        
        if status:
            save_reports(repo_path.name, status, REPORTS_DIR)
            all_repos_status.append({
                'name': status.name,
                'description': status.description,
                'created_at': status.created_at,
                'last_commit': status.last_commit,
                'total_commits': status.total_commits,
                'contributors': len(status.contributors)
            })
            print(f"✅ Generated reports for {status.name}")
    
    # Generate summary
    if all_repos_status:
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_repositories': len(all_repos_status),
            'repositories': all_repos_status
        }
        
        with open(REPORTS_DIR / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n🎉 Successfully generated reports for {len(all_repos_status)} repositories")
        print(f"📊 View reports in: {REPORTS_DIR}")
    else:
        print("❌ No repositories found or analyzed")

if __name__ == "__main__":
    main()
