#!/usr/bin/env python3
"""
WronAI Ecosystem Reporter

A lightweight tool to generate reports for all repositories in the WronAI ecosystem.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional
import markdown
from dataclasses import dataclass, asdict

# Configuration
BASE_DIR = Path('/home/tom/github/wronai')
REPORTS_DIR = BASE_DIR / '2025-06' / 'reports'
TEMPLATES_DIR = Path(__file__).parent / 'report_templates'

# Ensure directories exist
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

@dataclass
class RepoStats:
    name: str
    description: str
    last_commit: str
    commit_count: int
    author_counts: Dict[str, int]
    file_changes: Dict[str, int]
    languages: Dict[str, int]
    todos: List[str]

class RepoAnalyzer:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.now = datetime.now()
        self.month_ago = (self.now - timedelta(days=30)).strftime('%Y-%m-%d')
    
    def get_commit_history(self) -> List[Dict]:
        """Get commit history for the repository."""
        try:
            cmd = [
                'git', '-C', str(self.repo_path),
                'log',
                f'--since="{self.month_ago}"',
                '--pretty=format:{"hash":"%H","author":"%an","date":"%ad","message":"%s"}',
                '--date=short',
                '--numstat',
                '--no-merges'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return self._parse_git_log(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit history for {self.repo_path.name}: {e}")
            return []
    
    def _parse_git_log(self, log_output: str) -> List[Dict]:
        """Parse git log output into structured data."""
        commits = []
        current_commit = None
        
        for line in log_output.strip().split('\n'):
            line = line.strip()
            if line.startswith('{'):
                if current_commit:
                    commits.append(current_commit)
                try:
                    current_commit = json.loads(line)
                    current_commit['changes'] = []
                except json.JSONDecodeError:
                    current_commit = None
            elif line and current_commit and '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    current_commit['changes'].append({
                        'additions': parts[0],
                        'deletions': parts[1],
                        'file': parts[2]
                    })
        
        if current_commit:
            commits.append(current_commit)
        
        return commits
    
    def analyze(self) -> Optional[RepoStats]:
        """Analyze repository and return statistics."""
        print(f"Analyzing {self.repo_path.name}...")
        
        # Get commit history
        commits = self.get_commit_history()
        if not commits:
            return None
        
        # Calculate statistics
        author_counts = Counter()
        file_changes = Counter()
        languages = Counter()
        
        for commit in commits:
            author_counts[commit['author']] += 1
            for change in commit.get('changes', []):
                file_path = change.get('file', '')
                file_changes[file_path] += 1
                
                # Get file extension
                ext = os.path.splitext(file_path)[1].lower()
                if ext:
                    languages[ext] += 1
        
        # Get README content
        readme_content = self._get_readme_content()
        
        return RepoStats(
            name=self.repo_path.name,
            description=readme_content.get('description', 'No description'),
            last_commit=commits[0]['date'] if commits else 'N/A',
            commit_count=len(commits),
            author_counts=dict(author_counts.most_common(5)),
            file_changes=dict(file_changes.most_common(10)),
            languages=dict(languages.most_common(5)),
            todos=self._generate_todos(commits, file_changes)
        )
    
    def _get_readme_content(self) -> Dict[str, str]:
        """Extract content from README file."""
        readme = next((f for f in self.repo_path.glob('README*')), None)
        if readme and readme.is_file():
            try:
                with open(readme, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    return {
                        'description': first_line if first_line and not first_line.startswith('#') 
                                      else 'No description',
                        'has_readme': True
                    }
            except Exception as e:
                print(f"Error reading README: {e}")
        return {'description': 'No README found', 'has_readme': False}
    
    def _generate_todos(self, commits: List[Dict], file_changes: Dict) -> List[str]:
        """Generate TODO items based on repository analysis."""
        todos = []
        
        # Check for recent activity without tests
        recent_commits = commits[:10]  # Look at last 10 commits
        has_code_changes = any(
            any(not f['file'].endswith(('.md', '.txt')) for f in c.get('changes', []))
            for c in recent_commits
        )
        has_test_changes = any(
            'test' in f['file'].lower() for c in recent_commits 
            for f in c.get('changes', [])
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
    def generate_markdown(repo: RepoStats) -> str:
        """Generate markdown report for a repository."""
        return f"""# {repo.name}

**{repo.description}**

## 📊 Activity (Last 30 Days)

- **Last Commit:** {repo.last_commit}
- **Total Commits:** {repo.commit_count}

### Top Contributors
{"\n".join(f"- {author}: {count} commits" for author, count in repo.author_counts.items())}

### Most Active Files
{"\n".join(f"- {file}: {count} changes" for file, count in repo.file_changes.items())}

### Languages Used
{"\n".join(f"- {ext}: {count} files" for ext, count in repo.languages.items())}

## 📋 Next Steps
{"\n".join(f"- [ ] {todo}" for todo in repo.todos)}
"""

    @staticmethod
    def generate_json(repo: RepoStats) -> str:
        """Generate JSON report for a repository."""
        return json.dumps({
            'name': repo.name,
            'description': repo.description,
            'last_commit': repo.last_commit,
            'commit_count': repo.commit_count,
            'top_contributors': repo.author_counts,
            'active_files': repo.file_changes,
            'languages': repo.languages,
            'todos': repo.todos,
            'generated_at': datetime.now().isoformat()
        }, indent=2)

    @staticmethod
    def generate_html(repo: RepoStats) -> str:
        """Generate HTML report for a repository."""
        md_content = ReportGenerator.generate_markdown(repo)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the HTML with the content using f-strings
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{repo.name} - WronAI Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        pre {{ 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto;
            border-left: 3px solid #4e73df;
        }}
        code {{ 
            background: #f8f9fa; 
            padding: 2px 5px; 
            border-radius: 3px; 
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
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
    {html_content}
    <div class="footer">
        Generated on {timestamp} by WronAI Ecosystem Reporter
    </div>
</body>
</html>"""
        return html

def main():
    """Main function to generate reports for all repositories."""
    print("🚀 Starting WronAI Ecosystem Analysis")
    
    # Get all git repositories
    repos = [d for d in BASE_DIR.iterdir() 
             if d.is_dir() and (d / '.git').exists() and d.name != 'venv']
    
    all_reports = []
    
    for repo_path in repos:
        analyzer = RepoAnalyzer(repo_path)
        stats = analyzer.analyze()
        
        if stats:
            # Create report directory
            report_dir = REPORTS_DIR / stats.name
            report_dir.mkdir(exist_ok=True)
            
            # Generate reports
            with open(report_dir / 'report.md', 'w') as f:
                f.write(ReportGenerator.generate_markdown(stats))
            
            with open(report_dir / 'report.json', 'w') as f:
                f.write(ReportGenerator.generate_json(stats))
            
            with open(report_dir / 'index.html', 'w') as f:
                f.write(ReportGenerator.generate_html(stats))
            
            all_reports.append(stats)
            print(f"✅ Generated reports for {stats.name}")
    
    # Generate summary
    if all_reports:
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_repositories': len(all_reports),
            'repositories': [{
                'name': r.name,
                'last_commit': r.last_commit,
                'commit_count': r.commit_count,
                'top_contributor': next(iter(r.author_counts), None)
            } for r in all_reports]
        }
        
        with open(REPORTS_DIR / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n🎉 Successfully generated reports for {len(all_reports)} repositories")
        print(f"📊 View reports in: {REPORTS_DIR}")
    else:
        print("❌ No repositories found or analyzed")

if __name__ == "__main__":
    main()
