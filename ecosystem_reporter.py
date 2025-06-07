#!/usr/bin/env python3
import os
import json
import subprocess
import markdown
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
import shutil
import webbrowser
from jinja2 import Environment, FileSystemLoader

# Configuration
REPORTS_DIR = Path('/home/tom/github/wronai/2025-06/reports')
TEMPLATES_DIR = Path('/home/tom/github/wronai/2025-06/report_templates')
BASE_DIR = Path('/home/tom/github/wronai')

# Ensure directories exist
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
TEMPLATES_DIR.mkdir(exist_ok=True, parents=True)

@dataclass
class FileChange:
    path: str
    change_type: str
    additions: int = 0
    deletions: int = 0
    language: str = ""
    complexity: float = 0.0

@dataclass
class CommitStats:
    hash: str
    author: str
    date: str
    message: str
    changes: List[FileChange] = field(default_factory=list)
    is_feature: bool = False
    is_refactor: bool = False
    is_fix: bool = False
    impact_score: float = 0.0

@dataclass
class CodeMetrics:
    loc: int = 0
    complexity: float = 0.0
    test_coverage: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    tech_stack: Dict[str, int] = field(default_factory=dict)

@dataclass
class RepoAnalysis:
    name: str
    description: str
    last_updated: str
    total_commits: int
    recent_commits: List[CommitStats]
    active_days: Dict[str, int]
    top_contributors: Dict[str, int]
    file_changes: Dict[str, int]
    commit_trend: List[int]
    code_metrics: CodeMetrics
    todos: List[str]
    milestones: List[Dict[str, str]]
    health_score: float = 0.0

class RepoAnalyzer:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.now = datetime.now()
        self.week_ago = (self.now - timedelta(days=7)).strftime('%Y-%m-%d')
        self.month_ago = (self.now - timedelta(days=30)).strftime('%Y-%m-%d')
        
    def get_git_log(self) -> List[CommitStats]:
        # Implementation similar to previous version
        # ... (omitted for brevity, same as before)
        return []
    
    def analyze_codebase(self) -> CodeMetrics:
        metrics = CodeMetrics()
        try:
            # Count lines of code
            result = subprocess.run(
                ['tokei', '--json', str(self.repo_path)],
                capture_output=True, text=True, check=True
            )
            tokei_data = json.loads(result.stdout)
            
            # Process language stats
            for lang, stats in tokei_data.items():
                if isinstance(stats, dict) and 'code' in stats:
                    metrics.loc += stats['code']
                    metrics.tech_stack[lang] = stats['code']
            
            # Get dependencies (simplified example)
            requirements = self.repo_path / 'requirements.txt'
            if requirements.exists():
                with open(requirements, 'r') as f:
                    metrics.dependencies = [line.strip() for line in f if line.strip()]
            
            # Calculate complexity (simplified)
            metrics.complexity = min(metrics.loc / 1000, 10.0)  # Dummy complexity metric
            
            # Try to get test coverage if available
            coverage_file = self.repo_path / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    metrics.test_coverage = coverage_data.get('coverage', 0.0)
            
            return metrics
            
        except Exception as e:
            print(f"Error analyzing codebase: {str(e)}")
            return metrics
    
    def analyze(self) -> Optional[RepoAnalysis]:
        try:
            commits = self.get_git_log()
            if not commits:
                return None
                
            # Calculate metrics
            code_metrics = self.analyze_codebase()
            active_days = Counter(c.date for c in commits)
            contributors = Counter(c.author for c in commits)
            file_changes = Counter()
            
            for commit in commits:
                for change in commit.changes:
                    file_changes[change.path] += 1
            
            # Generate TODOs based on analysis
            todos = self.generate_todos(commits, code_metrics)
            
            # Calculate health score (0-100)
            health_score = self.calculate_health_score(commits, code_metrics, len(contributors))
            
            return RepoAnalysis(
                name=self.repo_path.name,
                description=self.get_repo_description(),
                last_updated=commits[0].date,
                total_commits=len(commits),
                recent_commits=commits[:10],
                active_days=dict(active_days.most_common(7)),
                top_contributors=dict(contributors.most_common(3)),
                file_changes=dict(file_changes.most_common(10)),
                commit_trend=[len([c for c in commits if c.date == d]) 
                             for d in sorted(set(c.date for c in commits))][-7:],
                code_metrics=code_metrics,
                todos=todos,
                milestones=self.generate_milestones(commits, code_metrics),
                health_score=health_score
            )
            
        except Exception as e:
            print(f"Error analyzing {self.repo_path.name}: {str(e)}")
            return None
    
    def generate_todos(self, commits: List[CommitStats], metrics: CodeMetrics) -> List[str]:
        todos = []
        
        # Check test coverage
        if metrics.test_coverage < 70:
            todos.append(f"Improve test coverage (currently {metrics.test_coverage:.1f}%)")
            
        # Check for recent features without tests
        if any(c.is_feature for c in commits[:5]) and not any('test' in f.path.lower() 
              for c in commits[:5] for f in c.changes):
            todos.append("Add tests for new features")
            
        # Check dependencies
        if len(metrics.dependencies) > 20:
            todos.append("Review and update dependencies")
            
        return todos
    
    def generate_milestones(self, commits: List[CommitStats], metrics: CodeMetrics) -> List[Dict[str, str]]:
        return [
            {"title": "Code Quality Improvements", "due": self.get_future_date(14)},
            {"title": "Test Coverage Target: 80%", "due": self.get_future_date(30)},
            {"title": "Performance Optimization", "due": self.get_future_date(60)}
        ]
    
    def get_future_date(self, days: int) -> str:
        return (self.now + timedelta(days=days)).strftime('%Y-%m-%d')
    
    def get_repo_description(self) -> str:
        readme = next((f for f in self.repo_path.glob('README*')), None)
        if readme and readme.is_file():
            with open(readme, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line and not first_line.startswith('#'):
                    return first_line
        return "No description available"
    
    def calculate_health_score(self, commits: List[CommitStats], 
                             metrics: CodeMetrics, num_contributors: int) -> float:
        """Calculate repository health score (0-100)"""
        score = 70  # Base score
        
        # Recent activity (up to +20)
        days_active = len(set(c.date for c in commits))
        score += min(20, days_active * 2)
        
        # Test coverage (up to +20)
        score += min(20, metrics.test_coverage * 0.2)
        
        # Multiple contributors (up to +10)
        score += min(10, num_contributors * 2)
        
        # Recent fixes (up to -20)
        recent_fixes = sum(1 for c in commits[:10] if c.is_fix)
        score -= min(20, recent_fixes * 2)
        
        return max(0, min(100, score))

class ReportGenerator:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.repos = [d for d in self.base_dir.iterdir() 
                     if d.is_dir() and (d / '.git').exists()]
        self.templates = self.setup_templates()
    
    def setup_templates(self) -> Environment:
        """Initialize Jinja2 templates"""
        if not TEMPLATES_DIR.exists():
            TEMPLATES_DIR.mkdir()
            
        # Create default templates if they don't exist
        default_templates = {
            'report.md': """# {{ repo.name }}

{{ repo.description }}

## 📊 Metrics
- **Health Score**: {{ "%.1f"|format(repo.health_score) }}/100
- **Last Updated**: {{ repo.last_updated }}
- **Total Commits**: {{ repo.total_commits }}
- **Lines of Code**: {{ repo.code_metrics.loc }}
- **Test Coverage**: {{ "%.1f"|format(repo.code_metrics.test_coverage) }}%

## 🚀 Recent Activity
{% for commit in repo.recent_commits %}
### {{ commit.message }}
- **Author**: {{ commit.author }}
- **Date**: {{ commit.date }}
- **Impact**: {{ "%.2f"|format(commit.impact_score) }}

Changes:
{% for change in commit.changes %}- {{ change.change_type }} {{ change.path }} (+{{ change.additions }}/-{{ change.deletions }})
{% endfor %}
{% endfor %}

## 📋 Next Steps
{% for todo in repo.todos %}- [ ] {{ todo }}
{% endfor %}
""",
            'report.json': """{
  "name": "{{ repo.name }}",
  "description": "{{ repo.description }}",
  "health_score": {{ "%.1f"|format(repo.health_score) }},
  "last_updated": "{{ repo.last_updated }}",
  "total_commits": {{ repo.total_commits }},
  "metrics": {
    "loc": {{ repo.code_metrics.loc }},
    "complexity": {{ "%.2f"|format(repo.code_metrics.complexity) }},
    "test_coverage": {{ "%.1f"|format(repo.code_metrics.test_coverage) }}
  },
  "top_contributors": {{ repo.top_contributors|tojson }},
  "tech_stack": {{ repo.code_metrics.tech_stack|tojson }}
}"""
        }
        
        for name, content in default_templates.items():
            path = TEMPLATES_DIR / name
            if not path.exists():
                with open(path, 'w') as f:
                    f.write(content)
        
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        env.filters['tojson'] = json.dumps
        return env
    
    def generate_reports(self):
        """Generate reports for all repositories"""
        all_reports = []
        
        for repo_path in self.repos:
            if repo_path.name == 'venv':
                continue
                
            print(f"Analyzing {repo_path.name}...")
            analyzer = RepoAnalyzer(repo_path)
            analysis = analyzer.analyze()
            
            if analysis:
                report_data = asdict(analysis)
                self.save_reports(repo_path.name, report_data)
                all_reports.append(report_data)
        
        # Generate summary report
        self.generate_summary_report(all_reports)
        
        # Generate dashboard
        self.generate_dashboard(all_reports)
    
    def save_reports(self, repo_name: str, data: dict):
        """Save reports in multiple formats"""
        repo_dir = REPORTS_DIR / repo_name
        repo_dir.mkdir(exist_ok=True)
        
        # Save markdown
        template = self.templates.get_template('report.md')
        with open(repo_dir / 'report.md', 'w') as f:
            f.write(template.render(repo=data))
        
        # Save JSON
        template = self.templates.get_template('report.json')
        with open(repo_dir / 'report.json', 'w') as f:
            f.write(template.render(repo=data))
        
        # Convert markdown to HTML
        self.convert_markdown_to_html(repo_dir / 'report.md', repo_dir / 'report.html')
    
    def convert_markdown_to_html(self, md_path: Path, html_path: Path):
        """Convert markdown to HTML"""
        try:
            with open(md_path, 'r') as f:
                md_content = f.read()
            html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
            
            # Wrap in HTML template
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Report - {title}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
{content}
</body>
</html>""".format(
                title=md_path.stem,
                content=html
            )
            
            with open(html_path, 'w') as f:
                f.write(html_content)
                
        except Exception as e:
            print(f"Error converting markdown to HTML: {str(e)}")
    
    def generate_summary_report(self, reports: List[dict]):
        """Generate a summary report across all repositories"""
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_repositories": len(reports),
            "total_loc": sum(r['code_metrics']['loc'] for r in reports),
            "avg_health_score": sum(r['health_score'] for r in reports) / len(reports) if reports else 0,
            "repositories": [{
                "name": r['name'],
                "health_score": r['health_score'],
                "loc": r['code_metrics']['loc'],
                "last_updated": r['last_updated']
            } for r in reports]
        }
        
        with open(REPORTS_DIR / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
    
    def generate_dashboard(self, reports: List[dict]):
        """Generate an HTML dashboard"""
        # Sort by health score
        reports_sorted = sorted(reports, key=lambda x: x['health_score'], reverse=True)
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>WronAI Ecosystem Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .repo-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .repo-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }}
        .health-score {{
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.9em;
            display: inline-block;
            margin-bottom: 10px;
        }}
        .health-high {{ background-color: #d4edda; color: #155724; }}
        .health-medium {{ background-color: #fff3cd; color: #856404; }}
        .health-low {{ background-color: #f8d7da; color: #721c24; }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 10px 0;
        }}
        .metric {{
            font-size: 0.9em;
        }}
        .metric .label {{
            color: #666;
            font-size: 0.8em;
        }}
        .chart-container {{
            margin: 30px 0;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        h2 {{ 
            color: #444;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        a {{ 
            color: #4a6baf;
            text-decoration: none;
        }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WronAI Ecosystem Dashboard</h1>
        <p>Last updated: {date}</p>
    </div>
    
    <div class="chart-container">
        <h2>Repository Health Overview</h2>
        <canvas id="healthChart"></canvas>
    </div>
    
    <h2>Repositories</h2>
    <div class="dashboard-grid">
        {"\n".join([self._generate_repo_card(r) for r in reports_sorted])}
    </div>
    
    <script>
        // Health chart
        const ctx = document.getElementById('healthChart').getContext('2d');
        const healthData = {{
            labels: {json.dumps([r['name'] for r in reports_sorted])},
            datasets: [{{
                label: 'Health Score',
                data: {json.dumps([r['health_score'] for r in reports_sorted])},
                backgroundColor: [
                    '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
                    '#5a5c69', '#858796', '#e83e8c', '#20c9a6', '#fd7e14'
                ],
                borderWidth: 1
            }}]
        }};
        
        new Chart(ctx, {{
            type: 'bar',
            data: healthData,
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'Health Score (0-100)'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return `Score: ${context.raw}`;
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>""".format(
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            json=json
        )
        
        with open(REPORTS_DIR / 'index.html', 'w') as f:
            f.write(html)
    
    def _generate_repo_card(self, repo: dict) -> str:
        """Generate HTML for a repository card"""
        health_class = 'health-high'
        if repo['health_score'] < 70:
            health_class = 'health-medium'
        if repo['health_score'] < 50:
            health_class = 'health-low'
            
        return f"""
        <div class="repo-card">
            <div class="health-score {health_class}">
                Health: {repo['health_score']:.1f}/100
            </div>
            <h3><a href="{repo['name']}/report.html">{repo['name']}</a></h3>
            <p>{repo['description']}</p>
            <div class="metrics">
                <div class="metric">
                    <div class="label">LOC</div>
                    <div>{repo['code_metrics']['loc']:,}</div>
                </div>
                <div class="metric">
                    <div class="label">Coverage</div>
                    <div>{repo['code_metrics']['test_coverage']:.1f}%</div>
                </div>
                <div class="metric">
                    <div class="label">Commits</div>
                    <div>{repo['total_commits']}</div>
                </div>
                <div class="metric">
                    <div class="label">Updated</div>
                    <div>{repo['last_updated']}</div>
                </div>
            </div>
        </div>
        """.format(repo=repo, health_class=health_class)

def setup_ci_cd():
    """Set up CI/CD configuration"""
    github_dir = BASE_DIR / '.github' / 'workflows'
    github_dir.mkdir(parents=True, exist_ok=True)
    
    # Create GitHub Actions workflow
    workflow = """name: WronAI Ecosystem Reports

on:
  schedule:
    - cron: '0 0 * * 1'  # Run weekly on Monday at midnight
  workflow_dispatch:  # Allow manual runs

jobs:
  generate-reports:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install markdown jinja2 tokei
    
    - name: Generate reports
      run: |
        cd 2025-06
        python ecosystem_reporter.py
    
    - name: Commit and push reports
      run: |
        git config --global user.name 'GitHub Actions'
        git config --global user.email 'actions@github.com'
        git add reports/
        git commit -m "docs: update ecosystem reports [skip ci]" || echo "No changes to commit"
        git push
"""
    
    with open(github_dir / 'ecosystem-reports.yml', 'w') as f:
        f.write(workflow)
    
    print(f"Created GitHub Actions workflow at: {github_dir}/ecosystem-reports.yml")

if __name__ == "__main__":
    # Set up CI/CD if not already done
    if not (BASE_DIR / '.github' / 'workflows' / 'ecosystem-reports.yml').exists():
        setup_ci_cd()
    
    # Generate reports
    generator = ReportGenerator(BASE_DIR)
    generator.generate_reports()
    
    print(f"\n🎉 Reports generated successfully!")
    print(f"📊 View dashboard: {REPORTS_DIR / 'index.html'}")
