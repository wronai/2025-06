"""
Report class for Weekly - represents the results of project analysis.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .project import Project


class CheckResult:
    """Represents the result of a single check."""
    
    def __init__(
        self,
        checker_name: str,
        title: str,
        status: str,
        details: str,
        suggestions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a check result.
        
        Args:
            checker_name: Name of the checker that produced this result
            title: Short title describing the check
            status: Status of the check (e.g., 'success', 'warning', 'error')
            details: Detailed description of the check results
            suggestions: List of suggested actions to improve the project
            metadata: Additional metadata about the check result
        """
        self.checker_name = checker_name
        self.title = title
        self.status = status
        self.details = details
        self.suggestions = suggestions or []
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the check result to a dictionary."""
        return {
            'checker_name': self.checker_name,
            'title': self.title,
            'status': self.status,
            'details': self.details,
            'suggestions': self.suggestions,
            'metadata': self.metadata
        }


class Report:
    """Represents a report of project analysis results."""
    
    def __init__(self, project: Project):
        """
        Initialize with the project being analyzed.
        
        Args:
            project: The project this report is for
        """
        self.project = project
        self.generated_at = datetime.utcnow()
        self.results: List[CheckResult] = []
        self.summary = {
            'total_checks': 0,
            'success': 0,
            'warnings': 0,
            'errors': 0,
        }
    
    def add_result(self, result: CheckResult) -> None:
        """
        Add a check result to the report.
        
        Args:
            result: The check result to add
        """
        self.results.append(result)
        self.summary['total_checks'] += 1
        
        # Update summary counts
        if result.status == 'success':
            self.summary['success'] += 1
        elif result.status == 'warning':
            self.summary['warnings'] += 1
        elif result.status == 'error':
            self.summary['errors'] += 1
    
    def get_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get all suggestions from the report.
        
        Returns:
            List of dictionaries containing suggestion details
        """
        suggestions = []
        for result in self.results:
            if result.suggestions:
                suggestions.append({
                    'checker': result.checker_name,
                    'title': result.title,
                    'suggestions': result.suggestions,
                    'status': result.status,
                })
        return suggestions
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the report to a dictionary.
        
        Returns:
            Dictionary representation of the report
        """
        return {
            'project': str(self.project.path),
            'generated_at': self.generated_at.isoformat(),
            'summary': self.summary,
            'results': [r.to_dict() for r in self.results],
            'suggestions': self.get_suggestions(),
        }
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert the report to a JSON string.
        
        Args:
            indent: Number of spaces to indent the JSON output
            
        Returns:
            JSON string representation of the report
        """
        import json
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_markdown(self) -> str:
        """
        Convert the report to a markdown string.
        
        Returns:
            Markdown representation of the report
        """
        lines = [
            f"# Project Analysis Report",
            f"**Project:** {self.project.path.name}",
            f"**Generated at:** {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- Total checks: {self.summary['total_checks']}",
            f"- ✅ Passed: {self.summary['success']}",
            f"- ⚠️ Warnings: {self.summary['warnings']}",
            f"- ❌ Errors: {self.summary['errors']}",
            "",
            "## Detailed Results",
        ]
        
        for result in self.results:
            status_icon = {
                'success': '✅',
                'warning': '⚠️',
                'error': '❌',
            }.get(result.status, 'ℹ️')
            
            lines.extend([
                f"### {status_icon} {result.title}",
                f"*{result.checker_name}*",
                "",
                result.details,
                "",
            ])
            
            if result.suggestions:
                lines.append("**Suggestions:**")
                for suggestion in result.suggestions:
                    lines.append(f"- {suggestion}")
                lines.append("")
        
        return "\n".join(lines)
