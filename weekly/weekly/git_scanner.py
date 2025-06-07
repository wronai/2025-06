"""Module for scanning Git repositories and generating reports."""
from __future__ import annotations

import os
import sys
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
import subprocess
import shlex
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

from weekly.checkers.base import CheckResult
from weekly.git_report import GitReportGenerator, RepoInfo, CheckResult as GitCheckResult


@dataclass
class GitRepo:
    """Represents a Git repository with its metadata."""
    
    path: Path
    name: str
    org: str = ""
    last_commit_date: Optional[datetime] = None
    has_changes: bool = False
    branch: str = "main"
    remote_url: str = ""
    
    def __post_init__(self):
        """Initialize repository metadata."""
        self.path = Path(self.path).resolve()
        self._extract_metadata()
    
    def _extract_metadata(self) -> None:
        """Extract metadata from the Git repository."""
        try:
            # Get the current branch
            result = self._run_git("rev-parse --abbrev-ref HEAD")
            if result.returncode == 0 and result.stdout.strip():
                self.branch = result.stdout.strip()
            
            # Get the last commit date
            result = self._run_git("log -1 --format=%cd --date=iso")
            if result.returncode == 0 and result.stdout.strip():
                self.last_commit_date = datetime.strptime(
                    result.stdout.strip().split()[0], 
                    "%Y-%m-%d"
                )
            
            # Get the remote URL
            result = self._run_git("remote get-url origin")
            if result.returncode == 0 and result.stdout.strip():
                self.remote_url = result.stdout.strip()
        except Exception as e:
            pass
    
    def has_recent_changes(self, since: datetime) -> bool:
        """Check if the repository has changes since a specific date."""
        if not self.last_commit_date:
            return False
        return self.last_commit_date >= since
    
    def _run_git(self, command: str) -> subprocess.CompletedProcess:
        """Run a git command in the repository."""
        try:
            return subprocess.run(
                ["git"] + shlex.split(command),
                cwd=self.path,
                capture_output=True,
                text=True,
                check=False
            )
        except Exception:
            return subprocess.CompletedProcess(args=command, returncode=1)


@dataclass
class ScanResult:
    """Represents the result of scanning a repository."""
    
    repo: GitRepo
    results: Dict[str, CheckResult] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert the result to a dictionary."""
        return {
            "repo": {
                "path": str(self.repo.path),
                "name": self.repo.name,
                "org": self.repo.org,
                "branch": self.repo.branch,
                "remote_url": self.repo.remote_url,
                "last_commit_date": self.repo.last_commit_date.isoformat() if self.repo.last_commit_date else None,
            },
            "results": {name: result.to_dict() for name, result in self.results.items()},
            "error": self.error,
        }


class GitScanner:
    """Scans Git repositories and generates reports."""
    
    def __init__(
        self,
        root_dir: Path,
        output_dir: Path,
        since: Optional[datetime] = None,
        recursive: bool = True,
        jobs: int = 4,
    ):
        """Initialize the scanner.
        
        Args:
            root_dir: Root directory to scan for Git repositories
            output_dir: Directory to save reports
            since: Only include repositories with changes since this date
            recursive: Whether to scan recursively
            jobs: Number of parallel jobs to use
        """
        self.root_dir = Path(root_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.since = since or (datetime.now() - timedelta(days=7))
        self.recursive = recursive
        self.jobs = jobs
        self.console = Console()
        self.report_generator = GitReportGenerator()
    
    def find_git_repos(self) -> List[GitRepo]:
        """Find all Git repositories in the root directory."""
        repos: List[GitRepo] = []
        
        if not self.root_dir.exists():
            self.console.print(f"[red]Error: Directory not found: {self.root_dir}")
            return repos
        
        self.console.print(f"[bold]Scanning for Git repositories in {self.root_dir}...")
        
        # Find all .git directories
        git_dirs = []
        for root, dirs, _ in os.walk(self.root_dir):
            if ".git" in dirs:
                git_dirs.append(Path(root))
                if not self.recursive:
                    dirs[:] = []  # Don't recurse further
        
        # Create GitRepo objects
        for git_dir in git_dirs:
            try:
                # Determine organization and repo name from path
                rel_path = git_dir.relative_to(self.root_dir)
                parts = list(rel_path.parts)
                
                org = parts[0] if len(parts) > 1 else ""
                repo_name = parts[-1]
                
                repo = GitRepo(path=git_dir, name=repo_name, org=org)
                
                # Skip if no recent changes and since is specified
                if self.since and not repo.has_recent_changes(self.since):
                    continue
                    
                repos.append(repo)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to process {git_dir}: {e}")
        
        return repos
    
    def scan_repo(self, repo: GitRepo) -> ScanResult:
        """Scan a single repository and return the results."""
        result = ScanResult(repo=repo)
        
        try:
            # Import checkers dynamically to avoid circular imports
            from weekly.checkers import (
                StyleChecker, 
                CodeQualityChecker, 
                DependenciesChecker,
                DocumentationChecker,
                TestChecker,
                CIChecker
            )
            
            checkers = [
                StyleChecker(),
                CodeQualityChecker(),
                DependenciesChecker(),
                DocumentationChecker(),
                TestChecker(),
                CIChecker(),
            ]
            
            # Run all checkers
            for checker in checkers:
                try:
                    check_result = checker.check(repo.path)
                    result.results[checker.name] = check_result
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Checker {checker.name} failed for {repo.path}: {e}")
            
            # Generate report for this repository
            self._generate_repo_report(repo, result)
            
        except Exception as e:
            result.error = str(e)
            self.console.print(f"[red]Error scanning {repo.path}: {e}")
        
        return result
    
    def scan_all(self) -> List[ScanResult]:
        """Scan all repositories and generate reports."""
        repos = self.find_git_repos()
        
        if not repos:
            self.console.print("[yellow]No Git repositories found.")
            return []
        
        self.console.print(f"[green]Found {len(repos)} repositories to scan.")
        
        results: List[ScanResult] = []
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Scan repositories in parallel
        with ThreadPoolExecutor(max_workers=self.jobs) as executor:
            futures = {executor.submit(self.scan_repo, repo): repo for repo in repos}
            
            with Progress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                BarColumn(),
                TaskProgressColumn(),
                console=self.console,
            ) as progress:
                task = progress.add_task("Scanning repositories...", total=len(futures))
                
                for future in as_completed(futures):
                    repo = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.console.print(f"[red]Error scanning {repo.path}: {e}")
                    
                    progress.update(task, advance=1, description=f"Scanned {repo.name}")
        
        # Generate summary report
        self._generate_summary_report(results)
        
        return results
    
    def _generate_repo_report(self, repo: GitRepo, result: ScanResult) -> Path:
        """Generate a report for a single repository.
        
        Args:
            repo: The Git repository
            result: Scan results for the repository
            
        Returns:
            Path to the generated report
        """
        # Create output directory
        output_dir = self.output_dir / repo.org / repo.name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate report filename with timestamp
        report_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path = output_dir / report_filename
        
        # Prepare repository info
        repo_info = RepoInfo(
            name=repo.name,
            org=repo.org,
            path=str(repo.path),
            branch=repo.branch,
            remote_url=repo.remote_url,
            last_commit_date=repo.last_commit_date.isoformat() if repo.last_commit_date else None,
            has_errors=result.error is not None or any(not r.is_ok for r in result.results.values())
        )
        
        # Convert check results to GitCheckResult format
        check_results = {}
        for name, check_result in result.results.items():
            check_results[name] = GitCheckResult(
                name=name,
                description=check_result.description,
                is_ok=check_result.is_ok,
                message=check_result.message,
                details=check_result.details,
                next_steps=check_result.next_steps or [],
                severity="high" if not check_result.is_ok else "low"
            )
        
        # Generate the report
        GitReportGenerator.generate_html_report(
            results=check_results,
            repo_info=repo_info,
            output_path=report_path,
            title=f"Weekly Report - {repo.org}/{repo.name}"
        )
        
        # Create a symlink to the latest report
        latest_link = output_dir / "latest.html"
        if latest_link.exists():
            latest_link.unlink()
        try:
            latest_link.symlink_to(report_path.name)
        except (FileExistsError, OSError):
            # Symlink might exist if running in parallel
            pass
            
        return report_path
    
    def _generate_summary_report(self, results: List[ScanResult]) -> Path:
        """Generate a summary report for all repositories.
        
        Args:
            results: List of scan results
            
        Returns:
            Path to the generated summary report
        """
        if not results:
            return None
            
        summary_path = self.output_dir / "summary.html"
        
        # Prepare repository data for the summary
        repos_data = []
        for result in results:
            has_errors = result.error is not None or any(not check.is_ok for check in result.results.values())
            
            # Generate the relative path to the repository's latest report
            rel_report_path = Path(result.repo.org) / result.repo.name / "latest.html"
            
            repos_data.append({
                "name": result.repo.name,
                "org": result.repo.org,
                "path": str(result.repo.path),
                "branch": result.repo.branch,
                "has_errors": has_errors,
                "last_commit": result.repo.last_commit_date.strftime("%Y-%m-%d %H:%M") if result.repo.last_commit_date else "Unknown",
                "report_path": str(rel_report_path),
                "remote_url": result.repo.remote_url
            })
        
        # Sort repos by organization and name
        repos_data.sort(key=lambda x: (x["org"].lower(), x["name"].lower()))
        
        # Generate the summary report
        GitReportGenerator.generate_summary_report(
            repos=repos_data,
            output_path=summary_path,
            title="Weekly Scan Summary",
            scan_date=datetime.now().strftime("%Y-%m-%d"),
            since_date=self.since.strftime("%Y-%m-%d") if self.since else None
        )
        
        return summary_path
            repo = result.repo
            summary_data.append({
                "name": f"{repo.org}/{repo.name}" if repo.org else repo.name,
                "path": str(repo.path),
                "branch": repo.branch,
                "last_commit": repo.last_commit_date.strftime("%Y-%m-%d") if repo.last_commit_date else "Unknown",
                "has_errors": any(not r.is_ok for r in result.results.values()),
                "report_path": f"{repo.org}/{repo.name}/latest.html" if repo.org else f"{repo.name}/latest.html"
            })
        
        # Generate the summary report
        self.report_generator.generate_summary(
            repos=summary_data,
            output_path=summary_path,
            title="Weekly Scan Summary",
            scan_date=datetime.now().strftime("%Y-%m-%d"),
            since_date=self.since.strftime("%Y-%m-%d") if self.since else None,
        )
        
        self.console.print(f"\n[green]✓ Generated summary report: {summary_path}")
