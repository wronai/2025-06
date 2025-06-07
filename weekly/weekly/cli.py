"""
Command-line interface for Weekly - A tool for analyzing Python project quality.
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import click

from rich.console import Console

from . import __version__, analyze_project
from .core.project import Project
from .core.report import Report
from .git_scanner import GitScanner

console = Console()

@click.group()
@click.version_option(version=__version__)
def main():
    """Weekly - Analyze your Python project's quality and get suggestions for improvement."""
    pass

@main.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, path_type=Path), 
                default='.')
@click.option('--format', '-f', 'output_format', type=click.Choice(['text', 'json', 'markdown'], case_sensitive=False),
              default='text', help='Output format (default: text)')
@click.option('--output', '-o', type=click.Path(writable=True, dir_okay=False, allow_dash=True),
              default='-', help='Output file (default: stdout)')
@click.option('--show-suggestions/--no-suggestions', default=True,
              help='Show improvement suggestions (default: true)')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def analyze(project_path: Path, output_format: str, output: str, show_suggestions: bool, verbose: bool):
    """
    Analyze a Python project and provide quality insights.
    
    PROJECT_PATH: Path to the project directory (default: current directory)
    """
    try:
        # Resolve the project path
        project_path = project_path.resolve()
        
        # Run the analysis
        if verbose:
            click.echo(f"🔍 Analyzing project at {project_path}...", err=True)
        
        report = analyze_project(project_path)
        
        # Prepare the output
        output_data = report.to_dict()
        
        # Format the output
        if output_format == 'json':
            result = json.dumps(output_data, indent=2)
        elif output_format == 'markdown':
            result = report.to_markdown()
        else:  # text format
            result = self._format_text_output(report, show_suggestions)
        
        # Write the output
        if output == '-':
            click.echo(result)
        else:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result, encoding='utf-8')
            if verbose:
                click.echo(f"📝 Report saved to {output_path}", err=True)
        
        # Exit with appropriate status code
        if output_data['summary']['errors'] > 0:
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def _format_text_output(self, report: 'Report', show_suggestions: bool = True) -> str:
    """Format the report as human-readable text."""
    lines = [
        f"📊 Weekly Project Analysis Report",
        "=" * 80,
        f"Project: {report.project.path.name}",
        f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    # Summary section
    lines.extend([
        "Summary:",
        "-" * 80,
        f"✅ {report.summary['success']} passed",
        f"⚠️  {report.summary['warnings']} warnings",
        f"❌ {report.summary['errors']} errors",
        ""
    ])
    
    # Results section
    lines.extend(["Detailed Results:", "-" * 80])
    
    for result in report.results:
        status_icon = {
            'success': '✅',
            'warning': '⚠️ ',
            'error': '❌',
            'suggestion': '💡'
        }.get(result.status.lower(), 'ℹ️ ')
        
        lines.extend([
            f"{status_icon} {result.title}",
            f"{' ' * 2}{result.details}",
        ])
        
        if show_suggestions and result.suggestions:
            lines.append("")
            lines.append(f"{' ' * 2}Suggestions:")
            for suggestion in result.suggestions:
                lines.append(f"{' ' * 4}• {suggestion}")
        
        lines.append("")
    
    # Suggestions section
    if show_suggestions:
        suggestions = report.get_suggestions()
        if suggestions:
            lines.extend(["Recommended Actions:", "-" * 80])
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"{i}. {suggestion['title']}")
                for s in suggestion['suggestions']:
                    lines.append(f"   • {s}")
                lines.append("")
    
    return "\n".join(lines)

@main.command()
@click.argument('root_dir', type=click.Path(exists=True, file_okay=False, path_type=Path), 
              default='.')
@click.option('--output', '-o', 'output_dir', type=click.Path(file_okay=False, path_type=Path),
              default='./weekly-reports', help='Output directory for reports (default: ./weekly-reports)')
@click.option('--since', '-s', 'since_str', type=str, 
              help='Only include repositories with changes since this date (e.g., "7 days ago", "2023-01-01")')
@click.option('--recursive/--no-recursive', default=True, 
              help='Scan directories recursively (default: true)')
@click.option('--jobs', '-j', type=int, default=4, 
              help='Number of parallel jobs (default: 4)')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['html', 'json', 'markdown'], case_sensitive=False),
              default='html', help='Output format (default: html)')
@click.option('--summary-only', is_flag=True, 
              help='Only generate a summary report, not individual reports for each repository')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def scan(
    root_dir: Path,
    output_dir: Path,
    since_str: Optional[str],
    recursive: bool,
    jobs: int,
    output_format: str,
    summary_only: bool,
    verbose: bool
):
    """
    Scan multiple Git repositories and generate quality reports.
    
    ROOT_DIR: Directory containing Git repositories to scan
    """
    try:
        # Parse since date
        since = None
        if since_str:
            if 'day' in since_str.lower():
                try:
                    days = int(since_str.split()[0])
                    since = datetime.now() - timedelta(days=days)
                except (ValueError, IndexError):
                    console.print(f"[yellow]Warning: Could not parse date '{since_str}'. Using default (7 days).[/]")
                    since = datetime.now() - timedelta(days=7)
            else:
                try:
                    since = datetime.strptime(since_str, '%Y-%m-%d')
                except ValueError:
                    console.print(f"[yellow]Warning: Invalid date format '{since_str}'. Use YYYY-MM-DD or 'N days ago'.[/]")
                    return 1
        
        if verbose:
            console.print(f"🔍 Scanning Git repositories in [bold]{root_dir}[/]")
            if since:
                console.print(f"📅 Showing changes since: {since.strftime('%Y-%m-%d')}")
            console.print(f"📁 Output directory: {output_dir.resolve()}")
            console.print(f"🔧 Jobs: {jobs}, Recursive: {recursive}, Format: {output_format}")
        
        # Create scanner
        scanner = GitScanner(
            root_dir=root_dir,
            output_dir=output_dir,
            since=since,
            recursive=recursive,
            jobs=jobs
        )
        
        # Run the scan
        results = scanner.scan_all()
        
        if not results:
            console.print("[yellow]No repositories found or no changes detected.[/]")
            return 0
        
        console.print(f"\n[green]✓ Generated reports for {len(results)} repositories[/]")
        console.print(f"📊 Summary report: {output_dir / 'summary.html'}")
        
        return 0
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    main()
