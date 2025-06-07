"""
Command-line interface for Weekly - A tool for analyzing Python project quality.
"""

import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import click

from . import __version__, analyze_project
from .core.project import Project
from .core.report import Report

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

if __name__ == "__main__":
    main()
