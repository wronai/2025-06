"""
Report generation module for weekly.
"""

import json
import markdown
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dataclasses import asdict

class ReportGenerator:
    """Class for generating reports from repository status."""
    
    @staticmethod
    def generate_markdown(status: 'RepoStatus') -> str:
        """Generate markdown report from status data."""
        return f"""# {status.name}

**{status.description}**

## 📊 Project Overview

- **Created:** {status.created_at[:10]}
- **Last Updated:** {status.last_commit[:10] if status.last_commit else 'N/A'}
- **Total Commits:** {status.total_commits}
- **Contributors:** {len(status.contributors)}

### Top Contributors
{"\n".join(f"- {author}: {count} commits" for author, count in status.contributors.items())}

### Most Active Files
{"\n".join(f"- `{file}`: {count} changes" for file, count in status.file_changes.items())}

### Languages Used
{"\n".join(f"- `{ext}`: {count} files" for ext, count in status.languages.items())}

## 📋 Next Steps
{"\n".join(f"- [ ] {todo}" for todo in status.todos)}

## 📜 Recent Commits

{"\n".join(f"- `{c['hash'][:7]}` {c['message']} ({c['date'][:10]})" for c in status.commits[:5])}

*[View full history in the JSON file]*
"""

    @classmethod
    def save_reports(cls, status: 'RepoStatus', output_dir: Path) -> None:
        """Save all report files to the specified directory.
        
        Args:
            status: The repository status to generate reports from
            output_dir: Directory to save the report files
        """
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate markdown content
        markdown_content = cls.generate_markdown(status)
        
        # Generate HTML content
        html_content = cls.generate_html(status, markdown_content)
        
        # Save JSON report
        json_path = output_dir / "status.json"
        with open(json_path, 'w') as f:
            json.dump(status.to_dict(), f, indent=2)
        
        # Save Markdown report
        md_path = output_dir / "status.md"
        with open(md_path, 'w') as f:
            f.write(markdown_content)
        
        # Save HTML report
        html_path = output_dir / "index.html"
        with open(html_path, 'w') as f:
            f.write(html_content)

    @staticmethod
    def generate_html(status: 'RepoStatus', markdown_content: str) -> str:
        """Generate HTML report with download option."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{status.name} - weekly Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        pre, code {{ 
            background: #f8f9fa;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        }}
        pre {{
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto;
            border-left: 3px solid #4e73df;
        }}
        code {{
            padding: 2px 5px; 
            border-radius: 3px; 
            font-size: 0.9em;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .download-btn {{
            background: #4e73df;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.9em;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 3px solid #4e73df;
        }}
        .metric-card h3 {{ margin: 0 0 10px 0; color: #4e73df; }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 0.9em;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{status.name}</h1>
        <a href="status.md" class="download-btn" download>Download Markdown</a>
    </div>
    
    <div class="content">
        {markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])}
    </div>
    
    <div class="footer">
        Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by weekly
    </div>
</body>
</html>"""

    @classmethod
    def save_reports(cls, status: 'RepoStatus', output_dir: Path):
        """Save all report files for a repository."""
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save status.json
        with open(output_dir / 'status.json', 'w') as f:
            json.dump(status.to_dict(), f, indent=2, default=str)
        
        # Generate and save markdown
        md_content = cls.generate_markdown(status)
        with open(output_dir / 'status.md', 'w') as f:
            f.write(md_content)
        
        # Generate and save HTML
        html_content = cls.generate_html(status, md_content)
        with open(output_dir / 'index.html', 'w') as f:
            f.write(html_content)
