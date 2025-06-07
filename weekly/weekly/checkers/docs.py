"""
Documentation checker for Weekly - checks for project documentation.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..core.project import Project
from ..core.report import CheckResult


class DocumentationChecker:
    """Checker for project documentation."""
    
    @property
    def name(self) -> str:
        return "documentation"
    
    @property
    def description(self) -> str:
        return "Checks for the presence and quality of project documentation"
    
    def check(self, project: Project) -> Optional[CheckResult]:
        """
        Check the project's documentation.
        
        Args:
            project: The project to check
            
        Returns:
            CheckResult with documentation-related findings
        """
        if not project.is_python_project:
            return None
            
        # Check for various documentation files
        readme = self._check_readme(project)
        license_file = self._check_license(project)
        changelog = self._check_changelog(project)
        contributing = self._check_contributing(project)
        code_of_conduct = self._check_code_of_conduct(project)
        api_docs = self._check_api_docs(project)
        
        missing_docs = []
        if not readme['exists']:
            missing_docs.append("README")
        if not license_file['exists']:
            missing_docs.append("LICENSE")
        if not changelog['exists']:
            missing_docs.append("CHANGELOG")
        if not contributing['exists']:
            missing_docs.append("CONTRIBUTING")
        if not code_of_conduct['exists']:
            missing_docs.append("CODE_OF_CONDUCT")
        
        if missing_docs:
            return CheckResult(
                checker_name=self.name,
                title="Missing important documentation files",
                status="warning",
                details=(
                    f"The following important documentation files are missing: {', '.join(missing_docs)}.\n"
                    "Good documentation helps users and contributors understand and work with your project."
                ),
                suggestions=[
                    f"Create a {doc} file" for doc in missing_docs
                ]
            )
        
        # Check README quality
        if readme['exists'] and readme['size'] < 500:  # Less than 500 bytes
            return CheckResult(
                checker_name=self.name,
                title="README could be more comprehensive",
                status="suggestion",
                details=(
                    "The README file is quite short. A good README should include:\n"
                    "- Project description and purpose\n"
                    "- Installation instructions\n"
                    "- Basic usage examples\n"
                    "- Contribution guidelines\n"
                    "- License information"
                ),
                suggestions=[
                    "Expand the README with more detailed information",
                    "Add installation and usage examples",
                    "Include badges for build status, coverage, etc."
                ]
            )
        
        # Check for API documentation
        if not api_docs['exists']:
            return CheckResult(
                checker_name=self.name,
                title="API documentation not found",
                status="suggestion",
                details=(
                    "No API documentation was found. Good API documentation helps users "
                    "understand how to use your code effectively."
                ),
                suggestions=[
                    "Add docstrings to your Python modules, classes, and functions",
                    "Consider using Sphinx or pdoc to generate API documentation",
                    "Add examples in your docstrings showing how to use your code"
                ]
            )
        
        # If we get here, documentation looks good
        return CheckResult(
            checker_name=self.name,
            title="Documentation looks good",
            status="success",
            details=(
                "All important documentation files were found. "
                f"README: {readme['size']} bytes, "
                f"LICENSE: {license_file['type'] if license_file['exists'] else 'missing'}, "
                f"CHANGELOG: {'present' if changelog['exists'] else 'missing'}, "
                f"API docs: {'present' if api_docs['exists'] else 'missing'}"
            ),
            suggestions=[
                "Consider adding more examples to your documentation",
                "Add a tutorial or quickstart guide for new users"
            ]
        )
    
    def _check_readme(self, project: Project) -> Dict[str, Any]:
        """Check for README file."""
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
        
        for readme in readme_files:
            readme_path = project.path / readme
            if readme_path.exists():
                return {
                    'exists': True,
                    'path': str(readme_path),
                    'size': readme_path.stat().st_size
                }
        
        return {'exists': False}
    
    def _check_license(self, project: Project) -> Dict[str, Any]:
        """Check for LICENSE file."""
        license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'COPYING']
        
        for license_file in license_files:
            license_path = project.path / license_file
            if license_path.exists():
                content = license_path.read_text(encoding='utf-8', errors='ignore')
                license_type = self._detect_license_type(content)
                return {
                    'exists': True,
                    'path': str(license_path),
                    'type': license_type or 'unknown'
                }
        
        return {'exists': False}
    
    def _detect_license_type(self, content: str) -> Optional[str]:
        """Detect the type of license from content."""
        content = content.lower()
        
        if 'apache license' in content or 'apache-2.0' in content:
            return 'Apache-2.0'
        elif 'mit license' in content or 'mit ' in content:
            return 'MIT'
        elif 'gnu general public license' in content or 'gpl' in content:
            if 'version 3' in content or 'v3' in content:
                return 'GPL-3.0'
            elif 'version 2' in content or 'v2' in content:
                return 'GPL-2.0'
            return 'GPL'
        elif 'bsd 3-clause' in content or 'revised bsd' in content:
            return 'BSD-3-Clause'
        elif 'bsd 2-clause' in content or 'simplified bsd' in content:
            return 'BSD-2-Clause'
        
        return None
    
    def _check_changelog(self, project: Project) -> Dict[str, bool]:
        """Check for CHANGELOG file."""
        changelog_files = ['CHANGELOG.md', 'CHANGELOG.rst', 'CHANGELOG.txt', 'CHANGELOG', 'HISTORY.md', 'HISTORY.rst', 'HISTORY']
        
        for changelog in changelog_files:
            if (project.path / changelog).exists():
                return {'exists': True}
        
        return {'exists': False}
    
    def _check_contributing(self, project: Project) -> Dict[str, bool]:
        """Check for CONTRIBUTING file."""
        contributing_files = ['CONTRIBUTING.md', 'CONTRIBUTING.rst', 'CONTRIBUTING.txt', 'CONTRIBUTING']
        
        for contributing in contributing_files:
            if (project.path / contributing).exists():
                return {'exists': True}
        
        return {'exists': False}
    
    def _check_code_of_conduct(self, project: Project) -> Dict[str, bool]:
        """Check for CODE_OF_CONDUCT file."""
        coc_files = ['CODE_OF_CONDUCT.md', 'CODE_OF_CONDUCT.rst', 'CODE_OF_CONDUCT.txt', 'CODE_OF_CONDUCT', 'CODE_OF_CONDUCT.md.txt']
        
        for coc in coc_files:
            if (project.path / coc).exists():
                return {'exists': True}
        
        return {'exists': False}
    
    def _check_api_docs(self, project: Project) -> Dict[str, bool]:
        """Check for API documentation."""
        # Check for Sphinx docs
        if (project.path / 'docs' / 'conf.py').exists():
            return {'exists': True}
            
        # Check for pdoc/autodoc in source files
        for py_file in project.path.glob('**/*.py'):
            content = project.get_file_content(str(py_file.relative_to(project.path)))
            if content and ("""""" in content or "'''" in content):
                return {'exists': True}
                
        # Check for doc/ directory with html files
        if any((project.path / 'doc').glob('*.html')):
            return {'exists': True}
            
        return {'exists': False}
