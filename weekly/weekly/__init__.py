"""
RepoFacts - A tool for generating comprehensive reports from Git repositories.
"""

__version__ = "0.1.0"

from .analyzer import GitAnalyzer, RepoStatus, CommitStats
from .reporter import ReportGenerator

__all__ = ['GitAnalyzer', 'RepoStatus', 'CommitStats', 'ReportGenerator']
