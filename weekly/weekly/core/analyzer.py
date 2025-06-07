"""
Core analysis functionality for Weekly.
"""
from pathlib import Path
from typing import List

from .project import Project
from .report import Report, CheckResult

# Import all checkers
from ..checkers.testing import TestChecker
from ..checkers.docs import DocumentationChecker
from ..checkers.ci_cd import CIChecker
from ..checkers.dependencies import DependenciesChecker
from ..checkers.code_quality import CodeQualityChecker

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
