#!/usr/bin/env python3
import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass, asdict

@dataclass
class FileChange:
    path: str
    change_type: str  # 'A'dded, 'M'odified, 'D'eleted
    additions: int = 0
    deletions: int = 0

@dataclass
class CommitStats:
    hash: str
    author: str
    date: str
    message: str
    changes: List[FileChange]
    is_feature: bool = False
    is_refactor: bool = False
    is_fix: bool = False

@dataclass
class RepoAnalysis:
    name: str
    description: str
    last_updated: str
    total_commits: int
    recent_commits: List[CommitStats]
    active_days: Dict[str, int]
    top_contributors: Dict[str, int]
    file_changes: Dict[str, int]
    commit_trend: List[int]
    tech_stack: Dict[str, int]
    todos: List[str]
    milestones: List[Dict[str, str]]

class GitAnalyzer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.repos = [d for d in self.base_dir.iterdir() 
                     if d.is_dir() and (d / '.git').exists()]
        self.week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
    def get_git_log(self, repo_path: Path) -> List[CommitStats]:
        try:
            # Get commit hashes and metadata
            cmd = [
                'git', '-C', str(repo_path),
                'log',
                '--since=1 week ago',
                '--pretty=format:{"hash":"%H","author":"%an","date":"%ad","message":"%s"}',
                '--date=short',
                '--numstat',
                '--no-merges'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            commits = []
            current_commit = None
            
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line.startswith('{'):
                    if current_commit:
                        commits.append(current_commit)
                    commit_data = json.loads(line)
                    current_commit = CommitStats(
                        hash=commit_data['hash'],
                        author=commit_data['author'],
                        date=commit_data['date'],
                        message=commit_data['message'],
                        changes=[],
                        is_feature=any(word in commit_data['message'].lower() 
                                     for word in ['feat', 'add', 'implement']),
                        is_refactor=any(word in commit_data['message'].lower() 
                                      for word in ['refactor', 'clean', 'update']),
                        is_fix=any(word in commit_data['message'].lower() 
                                 for word in ['fix', 'bug', 'error'])
                    )
                elif line and current_commit and '\t' in line:
                    # Parse numstat line: additions<tab>deletions<tab>file
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        add = int(parts[0]) if parts[0].isdigit() else 0
                        delete = int(parts[1]) if parts[1].isdigit() else 0
                        file_path = '\t'.join(parts[2:])  # In case filename contains tabs
                        change_type = 'A' if add > 0 and delete == 0 else 'D' if add == 0 and delete > 0 else 'M'
                        current_commit.changes.append(FileChange(
                            path=file_path,
                            change_type=change_type,
                            additions=add,
                            deletions=delete
                        ))
            
            if current_commit:
                commits.append(current_commit)
                
            return commits
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error processing git log for {repo_path.name}: {str(e)}")
            return []

    def analyze_repo(self, repo_path: Path) -> Optional[RepoAnalysis]:
        try:
            # Get basic repo info
            repo_name = repo_path.name
            print(f"\nAnalyzing {repo_name}...")
            
            # Get recent commits with detailed changes
            commits = self.get_git_log(repo_path)
            if not commits:
                return None
            
            # Calculate statistics
            active_days = defaultdict(int)
            contributors = defaultdict(int)
            file_changes = defaultdict(int)
            tech_stack = defaultdict(int)
            
            for commit in commits:
                active_days[commit.date] += 1
                contributors[commit.author] += 1
                
                for change in commit.changes:
                    file_changes[change.path] += 1
                    # Simple tech stack detection
                    ext = os.path.splitext(change.path)[1].lower()
                    if ext:
                        tech_stack[ext] += 1
            
            # Generate TODOs based on commit patterns
            todos = []
            if any(c.is_feature for c in commits) and not any('test' in f.path.lower() for c in commits for f in c.changes):
                todos.append("Add unit tests for new features")
            if any(c.is_fix for c in commits):
                todos.append("Verify fixes in different environments")
            
            # Generate milestones based on recent activity
            milestones = [
                {"title": "Complete current development cycle", "due": "2025-06-21"},
                {"title": "Perform integration testing", "due": "2025-06-28"},
                {"title": "Prepare next release", "due": "2025-07-05"}
            ]
            
            # Get repo description from README if available
            description = "No description available"
            readme_path = next((f for f in repo_path.glob('README*')), None)
            if readme_path and readme_path.is_file():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line and not first_line.startswith('#'):
                        description = first_line
            
            return RepoAnalysis(
                name=repo_name,
                description=description,
                last_updated=commits[0].date,
                total_commits=len(commits),
                recent_commits=commits[:5],  # Only include top 5 commits
                active_days=dict(active_days),
                top_contributors=dict(sorted(contributors.items(), key=lambda x: x[1], reverse=True)[:3]),
                file_changes=dict(sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:5]),
                commit_trend=[len([c for c in commits if c.date == d]) 
                             for d in sorted(set(c.date for c in commits))],
                tech_stack=dict(sorted(tech_stack.items(), key=lambda x: x[1], reverse=True)),
                todos=todos,
                milestones=milestones
            )
            
        except Exception as e:
            print(f"Error analyzing {repo_path.name}: {str(e)}")
            return None

    def generate_markdown_report(self, analysis: RepoAnalysis) -> str:
        md = f"# {analysis.name}\n\n"
        md += f"*{analysis.description}*\n\n"
        
        # Summary section
        md += "## 📊 Activity Summary\n\n"
        md += f"- **Last Updated**: {analysis.last_updated}\n"
        md += f"- **Total Commits (Last Week)**: {analysis.total_commits}\n"
        md += f"- **Active Days**: {len(analysis.active_days)} days\n"
        md += f"- **Top Contributors**: {', '.join(f'{k} ({v} commits)' for k, v in analysis.top_contributors.items())}\n\n"
        
        # Recent changes
        md += "## 📝 Recent Changes\n\n"
        for commit in analysis.recent_commits:
            emoji = "✨" if commit.is_feature else "🐛" if commit.is_fix else "🔧" if commit.is_refactor else "📝"
            md += f"### {emoji} {commit.message}\n"
            md += f"*{commit.date} by {commit.author}*\n"
            
            # Group changes by type
            changes_by_type = {'A': [], 'M': [], 'D': []}
            for change in commit.changes:
                changes_by_type[change.change_type].append(change)
            
            for change_type, changes in changes_by_type.items():
                if changes:
                    type_name = {'A': 'Added', 'M': 'Modified', 'D': 'Deleted'}[change_type]
                    md += f"- **{type_name}**:\n"
                    for change in changes:
                        md += f"  - `{change.path}`"
                        if change.additions or change.deletions:
                            md += f" (+{change.additions}/-{change.deletions})"
                        md += "\n"
            md += "\n"
        
        # Tech stack
        if analysis.tech_stack:
            md += "## 🛠️ Tech Stack\n\n"
            for ext, count in analysis.tech_stack.items():
                md += f"- `{ext}`: {count} files\n"
            md += "\n"
        
        # TODOs and Milestones
        if analysis.todos:
            md += "## 📋 Next Steps\n\n"
            for todo in analysis.todos:
                md += f"- [ ] {todo}\n"
            md += "\n"
        
        if analysis.milestones:
            md += "## 🎯 Milestones\n\n"
            for i, milestone in enumerate(analysis.milestones, 1):
                md += f"{i}. **{milestone['title']}** (Due: {milestone['due']})\n"
            md += "\n"
        
        return md

    def run_analysis(self):
        print(f"Analyzing {len(self.repos)} repositories...")
        
        # Create output directory
        output_dir = self.base_dir / '2025-06' / 'reports'
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate report for each repo
        for repo_path in self.repos:
            if repo_path.name == 'venv':  # Skip virtualenv
                continue
                
            analysis = self.analyze_repo(repo_path)
            if analysis:
                report = self.generate_markdown_report(analysis)
                report_path = output_dir / f"{analysis.name.lower().replace(' ', '_')}_report.md"
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(report)
        
        # Generate summary report
        self.generate_summary_report(output_dir)
        
        print(f"\nAnalysis complete. Reports saved to: {output_dir}")
    
    def generate_summary_report(self, output_dir: Path):
        # This would generate a cross-repo summary
        # Implementation would be similar to individual reports but aggregated
        pass

if __name__ == "__main__":
    analyzer = GitAnalyzer('/home/tom/github/wronai')
    analyzer.run_analysis()
