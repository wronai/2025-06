"""
Base checker class for Weekly project analysis.
"""
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.project import Project
from ..core.report import CheckResult


class CheckSeverity(str, Enum):
    """Enumeration of possible check severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseChecker(ABC):
    """Abstract base class for all project checkers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the checker."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a short description of what this checker does."""
        pass
    
    @abstractmethod
    def check(self, project: 'Project') -> Optional[CheckResult]:
        """
        Run the checker on the given project.
        
        Args:
            project: The project to check
            
        Returns:
            CheckResult with findings and suggestions, or None if not applicable
        """
        pass
    
    def _get_file_content(self, file_path: Path) -> Optional[str]:
        """Helper method to safely read file content."""
        try:
            if file_path.exists() and file_path.is_file():
                return file_path.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError):
            pass
        return None
