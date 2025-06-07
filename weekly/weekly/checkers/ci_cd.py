"""
CI/CD checker for Weekly - checks for continuous integration and deployment setup.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..core.project import Project
from ..core.report import CheckResult
from .base import BaseChecker


class CIChecker(BaseChecker):
    """Checker for CI/CD configuration."""
    
    @property
    def name(self) -> str:
        return "ci_cd"
    
    @property
    def description(self) -> str:
        return "Checks for continuous integration and deployment configuration"
    
    def check(self, project: Project) -> Optional[CheckResult]:
        """
        Check the project's CI/CD setup.
        
        Args:
            project: The project to check
            
        Returns:
            CheckResult with CI/CD-related findings
        """
        ci_config = self._detect_ci_config(project)
        cd_config = self._detect_cd_config(project)
        
        if not ci_config['exists'] and not cd_config['exists']:
            return CheckResult(
                checker_name=self.name,
                title="No CI/CD configuration found",
                status="warning",
                details=(
                    "No continuous integration or deployment configuration was detected.\n"
                    "CI/CD helps ensure code quality and automates the release process."
                ),
                suggestions=[
                    "Set up GitHub Actions by creating a .github/workflows directory",
                    "Consider using GitHub Actions, GitLab CI, or Travis CI",
                    "Add automated testing to your CI pipeline"
                ]
            )
        
        if ci_config['exists'] and not cd_config['exists']:
            return CheckResult(
                checker_name=self.name,
                title="CI configured but no CD detected",
                status="suggestion",
                details=(
                    f"CI is configured using {ci_config['type']}, but no continuous deployment "
                    "configuration was detected.\n"
                    "Automating deployments can save time and reduce errors."
                ),
                suggestions=[
                    f"Add deployment configuration to your {ci_config['type']} setup",
                    "Consider automating PyPI releases on version tags",
                    "Add deployment to staging/production environments"
                ]
            )
        
        if ci_config['exists'] and cd_config['exists']:
            suggestions = [
                "Add more test jobs to your CI pipeline (e.g., linting, type checking)",
                "Consider adding a test coverage report"
            ]
            
            # Check if testing is part of CI
            if not self._has_testing_in_ci(project, ci_config):
                suggestions.insert(0, "Add automated testing to your CI pipeline")
            
            return CheckResult(
                checker_name=self.name,
                title="CI/CD is properly configured",
                status="success",
                details=(
                    f"CI/CD is configured using {ci_config['type']}. "
                    f"Deployment is handled via {cd_config['type']}."
                ),
                suggestions=suggestions
            )
            
        return None
    
    def _detect_ci_config(self, project: Project) -> Dict[str, Any]:
        """Detect CI configuration files."""
        # GitHub Actions
        if (project.path / '.github' / 'workflows').exists():
            workflow_files = list((project.path / '.github' / 'workflows').glob('*.yml'))
            workflow_files += list((project.path / '.github' / 'workflows').glob('*.yaml'))
            
            if workflow_files:
                return {
                    'exists': True,
                    'type': 'GitHub Actions',
                    'path': str(project.path / '.github' / 'workflows'),
                    'files': [str(f.relative_to(project.path)) for f in workflow_files]
                }
        
        # GitLab CI
        gitlab_ci = project.path / '.gitlab-ci.yml'
        if gitlab_ci.exists():
            return {
                'exists': True,
                'type': 'GitLab CI',
                'path': str(gitlab_ci),
                'files': ['.gitlab-ci.yml']
            }
        
        # Travis CI
        travis_ci = project.path / '.travis.yml'
        if travis_ci.exists():
            return {
                'exists': True,
                'type': 'Travis CI',
                'path': str(travis_ci),
                'files': ['.travis.yml']
            }
        
        # CircleCI
        if (project.path / '.circleci' / 'config.yml').exists():
            return {
                'exists': True,
                'type': 'CircleCI',
                'path': str(project.path / '.circleci' / 'config.yml'),
                'files': ['.circleci/config.yml']
            }
        
        # Azure Pipelines
        azure_pipelines = project.path / 'azure-pipelines.yml'
        if azure_pipelines.exists():
            return {
                'exists': True,
                'type': 'Azure Pipelines',
                'path': str(azure_pipelines),
                'files': ['azure-pipelines.yml']
            }
        
        return {'exists': False}
    
    def _detect_cd_config(self, project: Project) -> Dict[str, Any]:
        """Detect CD configuration files."""
        # Check for deployment configurations in CI files
        ci_config = self._detect_ci_config(project)
        
        if ci_config['exists']:
            # Check for deployment steps in GitHub Actions
            if ci_config['type'] == 'GitHub Actions':
                for workflow_file in ci_config.get('files', []):
                    content = project.get_file_content(workflow_file)
                    if content and any(keyword in content.lower() for keyword in ['deploy', 'pypi', 'publish']):
                        return {
                            'exists': True,
                            'type': 'GitHub Actions',
                            'path': workflow_file
                        }
            
            # Check for deployment in other CI configs
            if ci_config['type'] in ['GitLab CI', 'Travis CI', 'CircleCI', 'Azure Pipelines']:
                content = project.get_file_content(ci_config['files'][0])
                if content and any(keyword in content.lower() for keyword in ['deploy', 'pypi', 'publish']):
                    return {
                        'exists': True,
                        'type': ci_config['type'],
                        'path': ci_config['files'][0]
                    }
        
        # Check for other deployment configs
        # Heroku
        if (project.path / 'app.json').exists() or (project.path / 'Procfile').exists():
            return {
                'exists': True,
                'type': 'Heroku',
                'path': 'app.json or Procfile'
            }
        
        # Docker
        if (project.path / 'Dockerfile').exists() or (project.path / 'docker-compose.yml').exists():
            return {
                'exists': True,
                'type': 'Docker',
                'path': 'Dockerfile or docker-compose.yml'
            }
        
        return {'exists': False}
    
    def _has_testing_in_ci(self, project: Project, ci_config: Dict[str, Any]) -> bool:
        """Check if testing is part of the CI configuration."""
        if not ci_config['exists']:
            return False
            
        # Check GitHub Actions
        if ci_config['type'] == 'GitHub Actions':
            for workflow_file in ci_config.get('files', []):
                content = project.get_file_content(workflow_file)
                if content and any(keyword in content.lower() for keyword in ['test', 'pytest', 'unittest', 'tox']):
                    return True
        
        # Check other CI configs
        elif ci_config['type'] in ['GitLab CI', 'Travis CI', 'CircleCI', 'Azure Pipelines']:
            content = project.get_file_content(ci_config['files'][0])
            if content and any(keyword in content.lower() for keyword in ['test', 'pytest', 'unittest', 'tox']):
                return True
        
        return False
