"""
Git scanner report generation module for Weekly.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field

class CheckResult:
    """Represents the result of a single check."""
    
    def __init__(
        self,
        name: str,
        description: str,
        is_ok: bool,
        message: str,
        details: Optional[Dict] = None,
        next_steps: Optional[List[str]] = None,
        severity: str = "medium"
    ):
        """Initialize a check result.
        
        Args:
            name: Name of the check
            description: Description of the check
            is_ok: Whether the check passed
            message: Result message
            details: Optional detailed results
            next_steps: List of suggested next steps
            severity: Severity level (low, medium, high)
        """
        self.name = name
        self.description = description
        self.is_ok = is_ok
        self.message = message
        self.details = details
        self.next_steps = next_steps or []
        self.severity = severity

@dataclass
class RepoInfo:
    """Repository information for reports."""
    name: str
    org: str = ""
    path: str = ""
    branch: str = "main"
    remote_url: str = ""
    last_commit_date: Optional[str] = None
    has_errors: bool = False

class GitReportGenerator:
    """Generates reports for Git repository scans."""
    
    @staticmethod
    def generate_html_report(
        results: Dict[str, CheckResult],
        repo_info: RepoInfo,
        output_path: Union[str, Path],
        title: str = "Weekly Git Report"
    ) -> None:
        """Generate an HTML report for a repository scan.
        
        Args:
            results: Dictionary of check results
            repo_info: Repository information
            output_path: Path to save the HTML report
            title: Report title
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare the context
        context = {
            "title": title,
            "repo_info": asdict(repo_info),
            "results": [{
                "name": name,
                "description": result.description,
                "is_ok": result.is_ok,
                "message": result.message,
                "details": json.dumps(result.details, indent=2) if result.details else None,
                "next_steps": result.next_steps,
                "severity": result.severity
            } for name, result in results.items()],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "has_errors": any(not result.is_ok for result in results.values())
        }
        
        # Generate the HTML
        html = GitReportGenerator._render_html_template("repo_report.html", context)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    @staticmethod
    def generate_summary_report(
        repos: List[Dict[str, Any]],
        output_path: Union[str, Path],
        title: str = "Weekly Scan Summary",
        scan_date: Optional[str] = None,
        since_date: Optional[str] = None
    ) -> None:
        """Generate a summary HTML report for multiple repositories.
        
        Args:
            repos: List of repository information dictionaries
            output_path: Path to save the HTML report
            title: Report title
            scan_date: Date of the scan (default: current date)
            since_date: Only include changes since this date
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare the context
        context = {
            "title": title,
            "repos": repos,
            "scan_date": scan_date or datetime.now().strftime("%Y-%m-%d"),
            "since_date": since_date,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Generate the HTML
        html = GitReportGenerator._render_html_template("summary_report.html", context)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    @staticmethod
    def _render_html_template(template_name: str, context: Dict[str, Any]) -> str:
        """Render an HTML template with the given context.
        
        Args:
            template_name: Name of the template file
            context: Dictionary of template variables
            
        Returns:
            Rendered HTML as a string
        """
        # This is a simplified version - in a real implementation, you would use a templating engine
        # like Jinja2 with proper template files
        
        if template_name == "repo_report.html":
            return GitReportGenerator._render_repo_report(context)
        elif template_name == "summary_report.html":
            return GitReportGenerator._render_summary_report(context)
        else:
            raise ValueError(f"Unknown template: {template_name}")
    
    @staticmethod
    def _render_repo_report(context: Dict[str, Any]) -> str:
        """Render the repository report template."""
        repo_info = context["repo_info"]
        results = context["results"]
        
        # Status badge
        status_badge = """
        <div class="status-badge">
            <span class="badge {badge_class}">{status_text}</span>
        </div>
        """.format(
            badge_class="badge-success" if not context["has_errors"] else "badge-error",
            status_text="All checks passed" if not context["has_errors"] else "Issues found"
        )
        
        # Results table
        results_table = ""
        for result in results:
            status_icon = "✓" if result["is_ok"] else "✗"
            status_class = "success" if result["is_ok"] else "error"
            
            details = f"<pre>{result['details']}</pre>" if result["details"] else ""
            next_steps = ""
            if result["next_steps"]:
                next_steps = "<ul>" + "".join(f"<li>{step}</li>" for step in result["next_steps"]) + "</ul>"
            
            results_table += f"""
            <tr class="{status_class}">
                <td>{result['name']}</td>
                <td><span class="status-icon">{status_icon}</span> {result['message']}</td>
                <td>{details}</td>
                <td>{next_steps}</td>
            </tr>
            """
        
        # Full HTML
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{context['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ margin-bottom: 30px; }}
                .repo-info {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .status-badge {{ margin: 10px 0; }}
                .badge {{ 
                    display: inline-block; 
                    padding: 5px 10px; 
                    border-radius: 3px; 
                    color: white; 
                    font-weight: bold; 
                }}
                .badge-success {{ background: #28a745; }}
                .badge-error {{ background: #dc3545; }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 20px 0;
                }}
                th, td {{ 
                    padding: 12px; 
                    text-align: left; 
                    border-bottom: 1px solid #ddd;
                }}
                th {{ background: #f5f5f5; }}
                tr.success {{ background: #f0fff0; }}
                tr.error {{ background: #fff0f0; }}
                .status-icon {{ font-weight: bold; }}
                pre {{ 
                    background: #f8f9fa; 
                    padding: 10px; 
                    border-radius: 3px; 
                    overflow-x: auto;
                    max-height: 200px;
                }}
                .footer {{ 
                    margin-top: 30px; 
                    text-align: center; 
                    color: #6c757d; 
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{context['title']}</h1>
                    <p>Generated on {context['timestamp']}</p>
                </div>
                
                <div class="repo-info">
                    <h2>{repo_info['org']}/{repo_info['name']}</h2>
                    <p>Branch: {repo_info['branch']}</p>
                    <p>Path: {repo_info['path']}</p>
                    {status_badge}
                </div>
                
                <h2>Check Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Check</th>
                            <th>Status</th>
                            <th>Details</th>
                            <th>Next Steps</th>
                        </tr>
                    </thead>
                    <tbody>
                        {results_table}
                    </tbody>
                </table>
                
                <div class="footer">
                    <p>Report generated by Weekly - {context['timestamp']}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _render_summary_report(context: Dict[str, Any]) -> str:
        """Render the summary report template."""
        repos = context["repos"]
        
        # Repo cards
        repo_cards = ""
        for repo in repos:
            status_icon = "✓" if not repo.get("has_errors", False) else "✗"
            status_class = "success" if not repo.get("has_errors", False) else "error"
            
            repo_cards += f"""
            <div class="repo-card">
                <h3>{repo['name']} <span class="status-icon {status_class}">{status_icon}</span></h3>
                <p>Branch: {repo.get('branch', 'main')}</p>
                <p>Last commit: {repo.get('last_commit', 'N/A')}</p>
                <p><a href="{repo.get('report_path', '#')}">View full report →</a></p>
            </div>
            """
        
        # Full HTML
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{context['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ margin-bottom: 30px; }}
                .summary-info {{ 
                    background: #f5f5f5; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin-bottom: 20px;
                    display: flex;
                    justify-content: space-between;
                }}
                .repo-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
                    gap: 20px; 
                    margin: 20px 0;
                }}
                .repo-card {{ 
                    background: white; 
                    border: 1px solid #ddd; 
                    border-radius: 5px; 
                    padding: 15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .repo-card h3 {{ margin-top: 0; }}
                .status-icon {{ 
                    font-weight: bold; 
                    margin-left: 5px;
                }}
                .status-icon.success {{ color: #28a745; }}
                .status-icon.error {{ color: #dc3545; }}
                .footer {{ 
                    margin-top: 30px; 
                    text-align: center; 
                    color: #6c757d; 
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{context['title']}</h1>
                    <p>Generated on {context['timestamp']}</p>
                </div>
                
                <div class="summary-info">
                    <div>
                        <h2>Scan Summary</h2>
                        <p>Repositories scanned: {len(repos)}</p>
                        {f"<p>Changes since: {context.get('since_date', 'N/A')}</p>" if context.get('since_date') else ''}
                    </div>
                </div>
                
                <h2>Repositories</h2>
                <div class="repo-grid">
                    {repo_cards}
                </div>
                
                <div class="footer">
                    <p>Report generated by Weekly - {context['timestamp']}</p>
                </div>
            </div>
        </body>
        </html>
        """
