"""
Repository status model for Weekly.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class RepoStatus:
    """Class representing repository status and statistics."""
    name: str
    description: str = ""
    created_at: str = ""
    last_commit: str = ""
    total_commits: int = 0
    contributors: Dict[str, int] = field(default_factory=dict)
    file_changes: Dict[str, int] = field(default_factory=dict)
    languages: Dict[str, int] = field(default_factory=dict)
    commits: List[Dict[str, Any]] = field(default_factory=list)
    todos: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "last_commit": self.last_commit,
            "total_commits": self.total_commits,
            "contributors": self.contributors,
            "file_changes": self.file_changes,
            "languages": self.languages,
            "commits": self.commits,
            "todos": self.todos,
            "generated_at": self.generated_at
        }
