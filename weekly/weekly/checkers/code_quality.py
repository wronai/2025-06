"""
Code quality checker for Weekly - checks code style and quality.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any, Set
import re

from ..core.project import Project
from ..core.report import CheckResult
from .base import BaseChecker


class CodeQualityChecker(BaseChecker):
    """Checker for code style and quality."""
    
    @property
    def name(self) -> str:
        return "code_quality"
    
    @property
    def description(self) -> str:
        return "Checks code style, formatting, and common quality issues"
    
    def check(self, project: Project) -> Optional[CheckResult]:
        """
        Check the project's code quality.
        
        Args:
            project: The project to check
            
        Returns:
            CheckResult with code quality findings
        """
        if not project.is_python_project:
            return None
            
        # Check for code formatters and linters
        formatters = self._detect_formatters(project)
        linters = self._detect_linters(project)
        type_checkers = self._detect_type_checkers(project)
        
        # Check for common issues
        issues = self._find_common_issues(project)
        
        # Prepare suggestions based on findings
        suggestions = []
        
        # Formatters
        if not formatters:
            suggestions.append("Add a code formatter like Black or autopep8")
        
        # Linters
        if not linters:
            suggestions.append("Add a linter like flake8, pylint, or ruff")
        
        # Type checkers
        if not type_checkers:
            suggestions.append("Add static type checking with mypy or pyright")
        
        # Issues found
        if issues:
            issue_descriptions = []
            
            if 'long_lines' in issues:
                issue_descriptions.append(f"{issues['long_lines']} lines exceed 100 characters")
                suggestions.append("Break long lines into multiple lines")
            
            if 'missing_docstrings' in issues:
                issue_descriptions.append(f"{issues['missing_docstrings']} functions/classes missing docstrings")
                suggestions.append("Add docstrings to all public functions and classes")
            
            if 'unused_imports' in issues:
                issue_descriptions.append(f"{len(issues['unused_imports'])} potentially unused imports")
                suggestions.append("Remove unused imports")
            
            if 'todo_comments' in issues:
                issue_descriptions.append(f"{len(issues['todo_comments'])} TODO/FIXME comments found")
                suggestions.append("Address TODO/FIXME comments or create issues for them")
            
            issues_text = ", ".join(issue_descriptions)
        else:
            issues_text = "No major code quality issues found"
        
        # Prepare details
        details = [
            "## Code Quality Tools",
            f"Formatters: {', '.join(formatters) if formatters else 'None detected'}",
            f"Linters: {', '.join(linters) if linters else 'None detected'}",
            f"Type checkers: {', '.join(type_checkers) if type_checkers else 'None detected'}",
            "",
            "## Issues",
            issues_text
        ]
        
        # Determine status
        if not formatters or not linters or not type_checkers or issues:
            status = "warning"
        else:
            status = "success"
        
        return CheckResult(
            checker_name=self.name,
            title="Code Quality Analysis",
            status=status,
            details="\n".join(details),
            suggestions=suggestions
        )
    
    def _detect_formatters(self, project: Project) -> List[str]:
        """Detect code formatters in the project."""
        formatters = []
        
        # Check pyproject.toml
        if project.pyproject and 'tool' in project.pyproject:
            if 'black' in project.pyproject['tool']:
                formatters.append("Black")
            if 'isort' in project.pyproject['tool']:
                formatters.append("isort")
        
        # Check setup.cfg
        if project.setup_cfg and any(section in project.setup_cfg for section in ['black', 'isort']):
            if 'black' in project.setup_cfg:
                formatters.append("Black")
            if 'isort' in project.setup_cfg:
                formatters.append("isort")
        
        # Check requirements
        deps = self._get_dependencies(project)
        all_deps = {dep[0].lower() for dep in deps['dependencies'] + deps['dev_dependencies']}
        
        if 'black' in all_deps:
            formatters.append("Black")
        if 'autopep8' in all_deps:
            formatters.append("autopep8")
        if 'yapf' in all_deps:
            formatters.append("YAPF")
        
        return sorted(list(set(formatters)))
    
    def _detect_linters(self, project: Project) -> List[str]:
        """Detect linters in the project."""
        linters = []
        
        # Check setup.cfg or tox.ini for linter configurations
        for config_file in ['setup.cfg', 'tox.ini']:
            content = project.get_file_content(config_file)
            if content:
                content = content.lower()
                if 'flake8' in content or '[flake8]' in content:
                    linters.append("Flake8")
                if 'pylint' in content or '[pylint]' in content:
                    linters.append("Pylint")
                if 'pylama' in content or '[pylama]' in content:
                    linters.append("Pylama")
        
        # Check requirements
        deps = self._get_dependencies(project)
        all_deps = {dep[0].lower() for dep in deps['dependencies'] + deps['dev_dependencies']}
        
        if 'flake8' in all_deps:
            linters.append("Flake8")
        if 'pylint' in all_deps:
            linters.append("Pylint")
        if 'pylama' in all_deps:
            linters.append("Pylama")
        if 'ruff' in all_deps:
            linters.append("Ruff")
        
        return sorted(list(set(linters)))
    
    def _detect_type_checkers(self, project: Project) -> List[str]:
        """Detect type checkers in the project."""
        type_checkers = []
        
        # Check mypy configuration
        if (project.path / 'mypy.ini').exists() or (project.path / '.mypy.ini').exists():
            type_checkers.append("mypy")
        
        # Check pyright configuration
        if (project.path / 'pyrightconfig.json').exists() or \
           (project.path / 'pyproject.toml').exists() and 'pyright' in str(project.pyproject):
            type_checkers.append("pyright")
        
        # Check requirements
        deps = self._get_dependencies(project)
        all_deps = {dep[0].lower() for dep in deps['dependencies'] + deps['dev_dependencies']}
        
        if 'mypy' in all_deps:
            type_checkers.append("mypy")
        if 'pyright' in all_deps:
            type_checkers.append("pyright")
        
        return sorted(list(set(type_checkers)))
    
    def _find_common_issues(self, project: Project) -> Dict[str, Any]:
        """Find common code quality issues."""
        issues = {}
        long_lines = 0
        missing_docstrings = 0
        unused_imports = set()
        todo_comments = []
        
        # Analyze Python files
        for py_file in project.path.glob('**/*.py'):
            if 'venv' in str(py_file) or '.tox' in str(py_file) or 'build' in str(py_file):
                continue
                
            content = project.get_file_content(str(py_file.relative_to(project.path)))
            if not content:
                continue
                
            lines = content.split('\n')
            
            # Check for long lines
            for i, line in enumerate(lines, 1):
                # Skip long strings and URLs
                if len(line) > 100 and not any(skip in line for skip in ['http://', 'https://', '"""', "'''"]):
                    long_lines += 1
            
            # Check for missing docstrings and TODO comments
            in_docstring = False
            in_class = False
            
            for i, line in enumerate(lines, 1):
                # Skip empty lines and comments
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    # Check for TODO/FIXME comments
                    if any(marker in stripped.lower() for marker in ['todo', 'fixme', 'xxx']):
                        todo_comments.append(f"{py_file.name}:{i} - {stripped}")
                    continue
                
                # Skip docstrings
                if '"""' in line or "'''" in line:
                    in_docstring = not in_docstring
                    continue
                
                if in_docstring:
                    continue
                
                # Check for class/function definitions
                if stripped.startswith('def ') or (stripped.startswith('async def ') and '):' in stripped):
                    # Check if next line is a docstring
                    next_line = lines[i] if i < len(lines) else ''
                    if not next_line.strip().startswith('"""'):
                        missing_docstrings += 1
                
                elif stripped.startswith('class ') and ':' in stripped:
                    # Check if next line is a docstring
                    next_line = lines[i] if i < len(lines) else ''
                    if not next_line.strip().startswith('"""'):
                        missing_docstrings += 1
            
            # Simple check for unused imports (very basic)
            imports = set()
            code_lines = []
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('import '):
                    for imp in stripped[7:].split(','):
                        imp = imp.strip().split(' as ')[0].split('.')[0]
                        imports.add(imp)
                elif stripped.startswith('from ') and ' import ' in stripped:
                    imp = stripped[5:].split(' import ')[0].strip()
                    imports.add(imp)
                else:
                    code_lines.append(line)
            
            # Check if imports are used in code
            code = '\n'.join(code_lines)
            for imp in list(imports):
                # Skip common built-ins and standard library modules
                if imp in ['os', 'sys', 'typing', 'pathlib', 're', 'json', 'datetime', 'logging']:
                    continue
                    
                # Simple check if the import is used in the code
                if not re.search(rf'\b{re.escape(imp)}\b', code):
                    unused_imports.add(f"{py_file.name}: {imp}")
        
        if long_lines > 0:
            issues['long_lines'] = long_lines
        if missing_docstrings > 0:
            issues['missing_docstrings'] = missing_docstrings
        if unused_imports:
            issues['unused_imports'] = sorted(list(unused_imports))
        if todo_comments:
            issues['todo_comments'] = todo_comments
        
        return issues
    
    def _get_dependencies(self, project: Project) -> Dict[str, List[tuple]]:
        """Helper to get dependencies from the project."""
        from .dependencies import DependenciesChecker
        checker = DependenciesChecker()
        return checker._get_dependencies(project)
