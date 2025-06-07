"""Style and formatting checker for Python projects."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from weekly.checkers.base import BaseChecker, CheckResult, CheckSeverity


@dataclass
class StyleIssue:
    """Represents a style issue found in the codebase."""
    
    file_path: str
    line: int
    column: int
    code: str
    message: str
    tool: str
    
    def to_dict(self) -> Dict[str, str | int]:
        """Convert the issue to a dictionary."""
        return {
            "file": str(self.file_path),
            "line": self.line,
            "column": self.column,
            "code": self.code,
            "message": self.message,
            "tool": self.tool,
        }


class StyleChecker(BaseChecker):
    """Checker for code style and formatting issues.
    
    This checker uses multiple tools to analyze code style:
    - Black: Code formatter
    - isort: Import sorter
    - flake8: Linter
    - pylint: Linter
    - mypy: Static type checker
    """
    
    name = "style"
    description = "Check code style and formatting"
    severity = CheckSeverity.MEDIUM
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the style checker.
        
        Args:
            config: Optional configuration dictionary for the checker
        """
        # Store config
        self.config = config or {}
        self.console = Console()
        self.issues: List[StyleIssue] = []
    
    def check(self, path: Path) -> CheckResult:
        """Run style checks on the given path."""
        self.console.print(f"[bold]Running style checks on {path}...")
        
        # Reset issues
        self.issues = []
        
        # Run all style checks
        self._run_black_check(path)
        self._run_isort_check(path)
        self._run_flake8_check(path)
        self._run_mypy_check(path)
        
        # Generate the report
        return self._generate_report()
    
    def _run_black_check(self, path: Path) -> None:
        """Run Black formatter check."""
        self.console.print("  - Checking code formatting with Black...")
        try:
            result = subprocess.run(
                ["black", "--check", "--diff", str(path)],
                capture_output=True,
                text=True,
                cwd=path.parent,
            )
            
            if result.returncode != 0:
                self._parse_black_output(result.stderr)
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.console.print(f"[yellow]Warning: Failed to run Black: {e}[/]")
    
    def _parse_black_output(self, output: str) -> None:
        """Parse Black output and extract issues."""
        for line in output.splitlines():
            if line.startswith("would reformat") or line.startswith("Oh no!") or "reformatted" in line:
                parts = line.split()
                if len(parts) > 1:
                    file_path = parts[-1]
                    self.issues.append(
                        StyleIssue(
                            file_path=file_path,
                            line=0,
                            column=0,
                            code="BLK100",
                            message="Code is not formatted with Black",
                            tool="black"
                        )
                    )
    
    def _run_isort_check(self, path: Path) -> None:
        """Run isort import sorter check."""
        self.console.print("  - Checking import sorting with isort...")
        try:
            result = subprocess.run(
                ["isort", "--check-only", "--diff", str(path)],
                capture_output=True,
                text=True,
                cwd=path.parent,
            )
            
            if result.returncode != 0:
                self._parse_isort_output(result.stderr)
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.console.print(f"[yellow]Warning: Failed to run isort: {e}[/]")
    
    def _parse_isort_output(self, output: str) -> None:
        """Parse isort output and extract issues."""
        for line in output.splitlines():
            if "ERROR:" in line and "Imports are incorrectly sorted" in line:
                file_path = line.split("ERROR: ")[1].split(": ")[0]
                self.issues.append(
                    StyleIssue(
                        file_path=file_path,
                        line=0,
                        column=0,
                        code="ISR100",
                        message="Imports are not properly sorted",
                        tool="isort"
                    )
                )
    
    def _run_flake8_check(self, path: Path) -> None:
        """Run flake8 linter check."""
        self.console.print("  - Running Flake8 linter...")
        try:
            result = subprocess.run(
                ["flake8", str(path)],
                capture_output=True,
                text=True,
                cwd=path.parent,
            )
            
            if result.returncode != 0:
                self._parse_flake8_output(result.stdout)
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.console.print(f"[yellow]Warning: Failed to run flake8: {e}[/]")
    
    def _parse_flake8_output(self, output: str) -> None:
        """Parse flake8 output and extract issues."""
        for line in output.strip().splitlines():
            # Skip empty lines and summary lines
            if not line.strip() or 'error:' in line or 'Found ' in line and 'error' in line:
                continue
                
            parts = line.split(":", 3)  # Split into max 4 parts
            if len(parts) >= 4:
                file_path = parts[0].strip()
                try:
                    line_num = int(parts[1].strip())
                    col_num = int(parts[2].strip())
                    # The rest is the message, which may contain colons
                    message_parts = parts[3].strip().split(None, 1)
                    if message_parts:
                        code = message_parts[0]
                        message = message_parts[1] if len(message_parts) > 1 else ""
                        
                        self.issues.append(
                            StyleIssue(
                                file_path=file_path,
                                line=line_num,
                                column=col_num,
                                code=code,
                                message=message,
                                tool="flake8"
                            )
                        )
                except (ValueError, IndexError) as e:
                    # Skip malformed lines
                    self.console.print(f"[yellow]Warning: Failed to parse flake8 output line: {line}[/]")
                    continue
    
    def _run_mypy_check(self, path: Path) -> None:
        """Run mypy static type checker."""
        self.console.print("  - Running mypy type checker...")
        try:
            result = subprocess.run(
                ["mypy", str(path)],
                capture_output=True,
                text=True,
                cwd=path.parent,
            )
            
            if result.returncode != 0:
                self._parse_mypy_output(result.stdout)
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.console.print(f"[yellow]Warning: Failed to run mypy: {e}[/]")
    
    def _parse_mypy_output(self, output: str) -> None:
        """Parse mypy output and extract issues."""
        for line in output.splitlines():
            line = line.strip()
            if not line or line.startswith("Found ") or line == "Success: no issues found in 1 source file":
                continue
                
            # Format: filename.py:line: error: Message
            if ": error:" in line or ": note:" in line:
                # Split on first 3 colons to separate file, line, type, and message
                parts = line.split(":", 3)
                
                if len(parts) >= 4:
                    file_path = parts[0].strip()
                    try:
                        line_num = int(parts[1].strip())
                        error_type = parts[2].strip()  # 'error' or 'note'
                        message = parts[3].strip()
                        
                        # If there's a code in brackets at the end, extract it
                        code = "TYP100"  # Default code
                        if "[" in message and "]" in message:
                            code = message[message.rfind("[")+1:message.rfind("]")]
                            message = message[:message.rfind("[")].strip()
                        
                        # Only add error issues, not notes
                        if error_type == "error":
                            self.issues.append(
                                StyleIssue(
                                    file_path=file_path,
                                    line=line_num,
                                    column=0,  # mypy doesn't provide column info
                                    code=code,
                                    message=message,
                                    tool="mypy"
                                )
                            )
                    except (ValueError, IndexError) as e:
                        # Skip lines that don't match the expected format
                        continue
    
    def _generate_report(self) -> 'CheckResult':
        """Generate a report from the collected issues."""
        from ..core.report import CheckResult
        
        if not self.issues:
            return CheckResult(
                checker_name=self.name,
                title="No Style Issues Found",
                status="success",
                details="No style issues found. Code follows style guidelines.",
                suggestions=[],
                metadata={"total_issues": 0, "issues_by_tool": {}}
            )
        
        # Group issues by tool
        issues_by_tool: Dict[str, List[StyleIssue]] = {}
        for issue in self.issues:
            if issue.tool not in issues_by_tool:
                issues_by_tool[issue.tool] = []
            issues_by_tool[issue.tool].append(issue)
        
        # Generate a detailed report
        details = [
            f"Found {len(self.issues)} total style issues across {len(issues_by_tool)} tools:"
        ]
        
        for tool, issues in sorted(issues_by_tool.items()):
            details.append(f"\n{tool.upper()}: {len(issues)} issues")
            for issue in issues[:5]:  # Show first 5 issues per tool
                details.append(f"  - {issue.file_path}:{issue.line}: {issue.message} ({issue.code})")
            if len(issues) > 5:
                details.append(f"  ... and {len(issues) - 5} more issues")
        
        # Generate next steps
        suggestions = [
            "Run 'black .' to automatically format your code",
            "Run 'isort .' to sort your imports",
            "Run 'flake8 .' to see detailed linting issues",
            "Run 'mypy .' to see detailed type checking issues",
        ]
        
        # Create a rich table for console output
        table = Table(title="Style Issues Summary")
        table.add_column("Tool", style="cyan")
        table.add_column("Issues", justify="right")
        table.add_column("Description")
        
        for tool, issues in sorted(issues_by_tool.items()):
            table.add_row(
                tool.upper(),
                str(len(issues)),
                f"Found {len(issues)} issue{'s' if len(issues) != 1 else ''} in {tool}"
            )
        
        # Print the table to console
        self.console.print()
        self.console.print(Panel.fit(table))
        
        return CheckResult(
            checker_name=self.name,
            title=f"Found {len(self.issues)} Style Issues",
            status="warning" if self.issues else "success",
            details="\n".join(details),
            suggestions=suggestions,
            metadata={
                "total_issues": len(self.issues),
                "issues_by_tool": {tool: len(issues) for tool, issues in issues_by_tool.items()}
            }
        )
    
    def get_fix_commands(self) -> List[Tuple[str, str]]:
        """Get commands to fix the detected issues."""
        return [
            ("Format code with Black", "black ."),
            ("Sort imports with isort", "isort ."),
            ("Run flake8 to see detailed issues", "flake8 ."),
            ("Run mypy to see type checking issues", "mypy ."),
        ]
