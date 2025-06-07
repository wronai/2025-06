"""
Project class for Weekly - represents a project to be analyzed.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
import toml
import yaml
import json

class Project:
    """Represents a project to be analyzed."""
    
    def __init__(self, path: Path):
        """
        Initialize with the project path.
        
        Args:
            path: Path to the project directory
        """
        self.path = Path(path).resolve()
        self._pyproject = None
        self._setup_py = None
        self._setup_cfg = None
        self._requirements_txt = None
        self._git_info = None
        
    @property
    def pyproject(self) -> Optional[Dict[str, Any]]:
        """Get the parsed pyproject.toml content if it exists."""
        if self._pyproject is None:
            pyproject_path = self.path / 'pyproject.toml'
            try:
                if pyproject_path.exists():
                    self._pyproject = toml.load(pyproject_path)
                else:
                    self._pyproject = {}
            except Exception:
                self._pyproject = {}
        return self._pyproject
    
    @property
    def setup_py(self) -> Optional[str]:
        """Get the content of setup.py if it exists."""
        if self._setup_py is None:
            setup_py_path = self.path / 'setup.py'
            self._setup_py = self._read_file(setup_py_path)
        return self._setup_py
    
    @property
    def setup_cfg(self) -> Optional[Dict[str, Any]]:
        """Get the parsed setup.cfg content if it exists."""
        if self._setup_cfg is None:
            setup_cfg_path = self.path / 'setup.cfg'
            try:
                if setup_cfg_path.exists():
                    self._setup_cfg = dict(toml.load(setup_cfg_path))
                else:
                    self._setup_cfg = {}
            except Exception:
                self._setup_cfg = {}
        return self._setup_cfg
    
    @property
    def requirements_txt(self) -> List[str]:
        """Get the list of requirements from requirements.txt if it exists."""
        if self._requirements_txt is None:
            req_path = self.path / 'requirements.txt'
            self._requirements_txt = []
            if req_path.exists():
                try:
                    content = req_path.read_text(encoding='utf-8')
                    self._requirements_txt = [
                        line.strip() 
                        for line in content.split('\n') 
                        if line.strip() and not line.strip().startswith('#')
                    ]
                except Exception:
                    pass
        return self._requirements_txt
    
    @property
    def has_tests(self) -> bool:
        """Check if the project has a tests directory."""
        return any(
            (self.path / d).is_dir() 
            for d in ['tests', 'test', 'testing']
        )
    
    @property
    def has_ci_config(self) -> bool:
        """Check if the project has CI configuration files."""
        ci_files = [
            '.github/workflows',
            '.gitlab-ci.yml',
            '.travis.yml',
            'azure-pipelines.yml',
            'circle/config.yml',
            'bitbucket-pipelines.yml',
        ]
        
        for ci_file in ci_files:
            if (self.path / ci_file).exists():
                return True
        return False
    
    @property
    def has_docs(self) -> bool:
        """Check if the project has documentation."""
        docs_dirs = ['docs', 'doc', 'documentation']
        return any((self.path / d).is_dir() for d in docs_dirs)
    
    @property
    def is_python_project(self) -> bool:
        """Check if this is a Python project."""
        return any(
            (self.path / f).exists() 
            for f in ['pyproject.toml', 'setup.py', 'setup.cfg']
        ) or any(f.suffix == '.py' for f in self.path.glob('**/*.py'))
    
    @property
    def uses_poetry(self) -> bool:
        """Check if the project uses Poetry for dependency management."""
        return 'tool' in (self.pyproject or {}) and 'poetry' in self.pyproject['tool']
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get the content of a file in the project.
        
        Args:
            file_path: Relative path to the file from the project root
            
        Returns:
            File content as string, or None if file doesn't exist or can't be read
        """
        path = self.path / file_path
        return self._read_file(path)
    
    def _read_file(self, path: Path) -> Optional[str]:
        """Helper method to safely read a file."""
        try:
            if path.exists() and path.is_file():
                return path.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError):
            pass
        return None
