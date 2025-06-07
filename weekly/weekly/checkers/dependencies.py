"""
Dependencies checker for Weekly - checks project dependencies and their health.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from ..core.project import Project
from ..core.report import CheckResult
from .base import BaseChecker


class DependenciesChecker(BaseChecker):
    """Checker for project dependencies."""
    
    @property
    def name(self) -> str:
        return "dependencies"
    
    @property
    def description(self) -> str:
        return "Checks project dependencies, their versions, and potential vulnerabilities"
    
    def check(self, project: Project) -> Optional[CheckResult]:
        """
        Check the project's dependencies.
        
        Args:
            project: The project to check
            
        Returns:
            CheckResult with dependencies-related findings
        """
        if not project.is_python_project:
            return None
            
        # Get dependencies from different sources
        deps = self._get_dependencies(project)
        
        if not deps['dependencies'] and not deps['dev_dependencies']:
            return CheckResult(
                checker_name=self.name,
                title="No dependencies specified",
                status="warning",
                details=(
                    "No dependencies were found in pyproject.toml, setup.py, or requirements.txt.\n"
                    "This might be correct if your project has no external dependencies."
                ),
                suggestions=[
                    "Add your project's dependencies to pyproject.toml or requirements.txt",
                    "If you're using setup.py, declare dependencies in setup_requires or install_requires"
                ]
            )
        
        # Check for unpinned dependencies
        unpinned = self._find_unpinned_dependencies(deps)
        
        if unpinned:
            return CheckResult(
                checker_name=self.name,
                title=f"Found {len(unpinned)} unpinned dependencies",
                status="warning",
                details=(
                    f"The following dependencies are not pinned to a specific version: {', '.join(unpinned)}.\n"
                    "Unpinned dependencies can lead to build inconsistencies and unexpected behavior."
                ),
                suggestions=[
                    f"Pin {dep} to a specific version (e.g., {dep}==1.2.3)" for dep in unpinned
                ] + ["Consider using a tool like pip-tools or poetry for dependency management"]
            )
        
        # Check for outdated dependencies (simulated - in a real implementation, this would check PyPI)
        outdated = self._find_outdated_dependencies(deps)
        
        if outdated:
            return CheckResult(
                checker_name=self.name,
                title=f"Found {len(outdated)} potentially outdated dependencies",
                status="suggestion",
                details=(
                    f"The following dependencies might be outdated: {', '.join(outdated)}.\n"
                    "Consider updating to the latest stable versions."
                ),
                suggestions=[
                    f"Check if there's a newer version of {dep} available" for dep in outdated
                ] + ["Run 'pip list --outdated' to check for outdated packages"]
            )
        
        # If we get here, dependencies look good
        return CheckResult(
            checker_name=self.name,
            title="Dependencies look good",
            status="success",
            details=(
                f"Found {len(deps['dependencies'])} runtime and {len(deps['dev_dependencies'])} development dependencies.\n"
                "All dependencies appear to be properly pinned."
            ),
            suggestions=[
                "Regularly update your dependencies to receive security fixes",
                "Consider using Dependabot or Renovate to automate dependency updates"
            ]
        )
    
    def _get_dependencies(self, project: Project) -> Dict[str, List[Tuple[str, str]]]:
        """
        Extract dependencies from various project files.
        
        Returns:
            Dict with 'dependencies' and 'dev_dependencies' lists of (name, constraint) tuples
        """
        result = {
            'dependencies': [],
            'dev_dependencies': []
        }
        
        # Check pyproject.toml (PEP 621 or Poetry)
        if project.pyproject:
            # Poetry
            if 'tool' in project.pyproject and 'poetry' in project.pyproject['tool']:
                poetry = project.pyproject['tool']['poetry']
                
                # Main dependencies
                if 'dependencies' in poetry:
                    for name, spec in poetry['dependencies'].items():
                        if name.lower() != 'python':
                            constraint = self._normalize_constraint(spec) if isinstance(spec, str) else 'any'
                            result['dependencies'].append((name, constraint))
                
                # Dev dependencies
                if 'dev-dependencies' in poetry:
                    for name, spec in poetry['dev-dependencies'].items():
                        constraint = self._normalize_constraint(spec) if isinstance(spec, str) else 'any'
                        result['dev_dependencies'].append((name, constraint))
                
                # Extras
                if 'extras' in poetry:
                    for extra_name, deps in poetry['extras'].items():
                        for dep in deps:
                            name, _, constraint = self._parse_dep_spec(dep)
                            result['dependencies'].append((name, constraint or 'any'))
            
            # PEP 621
            elif 'project' in project.pyproject:
                project_config = project.pyproject['project']
                
                # Dependencies
                if 'dependencies' in project_config:
                    for dep in project_config['dependencies']:
                        name, _, constraint = self._parse_dep_spec(dep)
                        result['dependencies'].append((name, constraint or 'any'))
                
                # Optional dependencies
                if 'optional-dependencies' in project_config:
                    for extra_name, deps in project_config['optional-dependencies'].items():
                        for dep in deps:
                            name, _, constraint = self._parse_dep_spec(dep)
                            result['dependencies'].append((name, constraint or 'any'))
        
        # Check setup.py (simple regex-based parsing)
        if project.setup_py:
            # This is a very simplified parser and might miss some edge cases
            content = project.setup_py.lower()
            
            # Look for install_requires
            if 'install_requires' in content:
                # This is a very naive approach - a real implementation would need to parse the Python AST
                pass
        
        # Check requirements.txt
        if project.requirements_txt:
            for dep in project.requirements_txt:
                name, _, constraint = self._parse_dep_spec(dep)
                if name and name.lower() not in ['-e', '--editable']:
                    result['dependencies'].append((name, constraint or 'any'))
        
        return result
    
    def _parse_dep_spec(self, spec: str) -> Tuple[str, str, str]:
        """Parse a dependency specification into (name, version_spec, extras)."""
        # Remove whitespace and comments
        spec = spec.split('#')[0].strip()
        if not spec:
            return '', '', ''
        
        # Handle extras
        extras = ''
        if '[' in spec and ']' in spec:
            start = spec.find('[')
            end = spec.find(']')
            extras = spec[start+1:end]
            spec = spec[:start] + spec[end+1:]
        
        # Split on comparison operators
        for op in ['==', '>=', '<=', '>', '<', '~=', '!=']:
            if op in spec:
                name, version = spec.split(op, 1)
                return name.strip(), op, version.strip()
        
        # No version specified
        return spec.strip(), '', ''
    
    def _normalize_constraint(self, constraint: str) -> str:
        """Normalize version constraints for comparison."""
        # This is a simplified version - a real implementation would need to handle all cases
        constraint = constraint.strip()
        
        if not constraint or constraint == '*':
            return 'any'
        
        # Remove spaces around comparison operators
        for op in ['==', '>=', '<=', '>', '<', '~=', '!=']:
            if op in constraint:
                name, version = constraint.split(op, 1)
                return f"{name.strip()}{op}{version.strip()}"
        
        return constraint
    
    def _find_unpinned_dependencies(self, deps: Dict[str, List[Tuple[str, str]]]) -> List[str]:
        """Find dependencies that don't have version constraints."""
        unpinned = []
        
        for dep_type in ['dependencies', 'dev_dependencies']:
            for name, constraint in deps[dep_type]:
                if constraint == 'any' and name not in [d[0] for d in unpinned]:
                    unpinned.append((name, constraint))
        
        # Sort by name for consistent output
        return sorted([dep[0] for dep in unpinned])
    
    def _find_outdated_dependencies(self, deps: Dict[str, List[Tuple[str, str]]]) -> List[str]:
        """Find potentially outdated dependencies."""
        # In a real implementation, this would check PyPI or a vulnerability database
        # For now, we'll just return an empty list
        return []
