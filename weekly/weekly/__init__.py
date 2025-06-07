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
from .core.analyzer import analyze_project
from .core.repo_status import RepoStatus
from .git_analyzer import GitAnalyzer, CommitStats

# Import Git scanner and report generator
from .git_scanner import GitRepo, GitScanner, ScanResult
from .git_report import GitReportGenerator, RepoInfo, CheckResult as GitCheckResult

# Import and expose CLI
from .cli import main

__all__ = [
    # Core functionality
    'analyze_project',
    'Project',
    'Report',
    'RepoStatus',
    'GitAnalyzer',
    'CommitStats',
    'main',  # Export main as cli
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


