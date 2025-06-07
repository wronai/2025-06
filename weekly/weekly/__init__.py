"""
Weekly - A tool for analyzing project quality and suggesting next steps.
"""

__version__ = "0.1.0"

from pathlib import Path
from typing import List, Dict, Any, Optional

# Import checkers
from .checkers.base import BaseChecker
from .checkers.testing import TestChecker
from .checkers.docs import DocumentationChecker
from .checkers.ci_cd import CIChecker
from .checkers.dependencies import DependenciesChecker
from .checkers.code_quality import CodeQualityChecker
from .checkers.style import StyleChecker

# Import core components
from .core.project import Project
from .core.report import Report, CheckResult

# Import Git scanner and report generator
from .git_scanner import GitRepo, GitScanner, ScanResult
from .git_report import GitReportGenerator, RepoInfo, CheckResult as GitCheckResult

__all__ = [
    # Core functionality
    'analyze_project',
    'Project',
    'Report',
    'CheckResult',
    
    # Checkers
    'BaseChecker',
    'TestChecker',
    'DocumentationChecker',
    'CIChecker',
    'DependenciesChecker',
    'CodeQualityChecker',
    'StyleChecker',
    
    # Git scanning
    'GitRepo',
    'GitScanner',
    'ScanResult',
    'GitReportGenerator',
    'RepoInfo',
    'GitCheckResult',
]

def analyze_project(project_path: Path) -> Report:
    """
    Analyze a project and generate a report with suggested next steps.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Report: A report containing analysis results and suggestions
    """
    project = Project(project_path)
    report = Report(project)
    
    # Register all available checkers
    checkers = [
        TestChecker(),
        DocumentationChecker(),
        CIChecker(),
        DependenciesChecker(),
        CodeQualityChecker(),
    ]
    
    # Run all checkers
    for checker in checkers:
        try:
            result = checker.check(project)
            if result:
                report.add_result(result)
        except Exception as e:
            # Log the error but continue with other checkers
            print(f"Error running {checker.__class__.__name__}: {str(e)}")
    
    return report
