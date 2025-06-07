"""
Command-line interface for RepoFacts.
"""

import sys
import json
from pathlib import Path
from typing import List, Optional
import click

from .analyzer import GitAnalyzer, RepoStatus
from .reporter import ReportGenerator

@click.group()
@click.version_option()
def cli():
    """RepoFacts - Generate comprehensive reports from Git repositories."""
    pass

@cli.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--output', '-o', type=click.Path(file_okay=False, path_type=Path), 
              default='./reports', help='Output directory for reports')
def analyze(repo_path: Path, output: Path):
    """Analyze a single repository and generate reports."""
    analyzer = GitAnalyzer(repo_path)
    status = analyzer.analyze()
    
    if status:
        output_dir = output / repo_path.name
        ReportGenerator.save_reports(status, output_dir)
        click.echo(f"✅ Generated reports for {repo_path.name} in {output_dir}")
    else:
        click.echo(f"❌ Failed to analyze repository: {repo_path}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('org_path', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--output', '-o', type=click.Path(file_okay=False, path_type=Path), 
              default='./reports', help='Output directory for reports')
def analyze_org(org_path: Path, output: Path):
    """Analyze all repositories in an organization directory."""
    repos = [d for d in org_path.iterdir() 
             if d.is_dir() and (d / '.git').exists() and d.name != 'venv']
    
    if not repos:
        click.echo(f"❌ No Git repositories found in {org_path}", err=True)
        sys.exit(1)
    
    all_repos_status = []
    
    for repo_path in repos:
        analyzer = GitAnalyzer(repo_path)
        status = analyzer.analyze()
        
        if status:
            repo_output = output / repo_path.name
            ReportGenerator.save_reports(status, repo_output)
            all_repos_status.append({
                'name': status.name,
                'description': status.description,
                'created_at': status.created_at,
                'last_commit': status.last_commit,
                'total_commits': status.total_commits,
                'contributors': len(status.contributors)
            })
            click.echo(f"✅ Generated reports for {status.name}")
    
    # Save summary
    if all_repos_status:
        summary = {
            'generated_at': RepoStatus.generated_at,
            'total_repositories': len(all_repos_status),
            'repositories': all_repos_status
        }
        
        output.mkdir(parents=True, exist_ok=True)
        with open(output / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        click.echo(f"\n🎉 Successfully generated reports for {len(all_repos_status)} repositories")
        click.echo(f"📊 View reports in: {output.absolute()}")

if __name__ == "__main__":
    cli()
