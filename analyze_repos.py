import os
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

def get_git_log(repo_path):
    try:
        cmd = [
            'git', '-C', repo_path,
            'log',
            '--since=1 week ago',
            '--pretty=format:{"commit": "%H", "author": "%an", "date": "%ad", "message": "%s"}',
            '--date=iso'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Parse the git log output
        log_entries = []
        for line in result.stdout.strip().split('\n'):
            try:
                entry = json.loads(line)
                log_entries.append(entry)
            except json.JSONDecodeError:
                continue
        return log_entries
    except subprocess.CalledProcessError:
        return []

def analyze_repo(repo_path):
    repo_name = os.path.basename(repo_path)
    print(f"\nAnalyzing {repo_name}...")
    
    # Get recent commits
    commits = get_git_log(repo_path)
    
    if not commits:
        print("  No recent activity")
        return {
            'name': repo_name,
            'recent_commits': [],
            'summary': 'No recent activity',
            'todos': [],
            'milestones': []
        }
    
    # Analyze commit messages
    features = set()
    fixes = set()
    refactors = set()
    
    for commit in commits:
        msg = commit['message'].lower()
        if 'fix' in msg or 'bug' in msg:
            fixes.add(commit['message'])
        elif 'feat' in msg or 'add' in msg or 'implement' in msg:
            features.add(commit['message'])
        elif 'refactor' in msg or 'clean' in msg or 'update' in msg:
            refactors.add(commit['message'])
    
    # Generate summary
    summary = []
    if features:
        summary.append(f"Added {len(features)} new features")
    if fixes:
        summary.append(f"Fixed {len(fixes)} issues")
    if refactors:
        summary.append(f"Refactored {len(refactors)} components")
    
    # Generate TODOs based on recent activity
    todos = []
    if 'test' not in '\n'.join([m.lower() for m in features]):
        todos.append("Add unit tests for new features")
    if fixes:
        todos.append("Verify all fixes in different environments")
    
    # Generate milestones
    milestones = [
        "Complete current feature development",
        "Perform integration testing",
        "Prepare for next release"
    ]
    
    return {
        'name': repo_name,
        'recent_commits': commits[:3],  # Show only first 3 commits
        'summary': '; '.join(summary) if summary else 'Maintenance updates',
        'todos': todos,
        'milestones': milestones
    }

if __name__ == "__main__":
    base_dir = Path('/home/tom/github/wronai')
    all_repos = [d for d in base_dir.iterdir() if d.is_dir() and (d / '.git').exists()]
    
    print(f"Analyzing {len(all_repos)} repositories...")
    
    results = []
    for repo in all_repos:
        if repo.name == 'venv':  # Skip virtualenv
            continue
        try:
            result = analyze_repo(str(repo))
            results.append(result)
        except Exception as e:
            print(f"Error analyzing {repo.name}: {str(e)}")
    
    # Save results to a markdown file
    output_file = base_dir / '2025-06' / 'weekly_report.md'
    with open(output_file, 'w') as f:
        f.write("# Weekly Development Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Overview\n")
        active_repos = [r for r in results if r['recent_commits']]
        f.write(f"Active repositories this week: {len(active_repos)}/{len(results)}\n\n")
        
        f.write("## Repository Details\n")
        for repo in results:
            f.write(f"### {repo['name']}\n")
            f.write(f"**Summary**: {repo['summary']}\n\n")
            
            if repo['recent_commits']:
                f.write("**Recent Activity**:\n")
                for commit in repo['recent_commits']:
                    f.write(f"- {commit['date'][:10]}: {commit['message']} ({commit['author']})\n")
            
            if repo['todos']:
                f.write("\n**TODO**:\n")
                for todo in repo['todos']:
                    f.write(f"- [ ] {todo}\n")
            
            if repo['milestones']:
                f.write("\n**Milestones**:\n")
                for i, milestone in enumerate(repo['milestones'], 1):
                    f.write(f"{i}. {milestone}\n")
            
            f.write("\n---\n\n")
    
    print(f"\nReport generated: {output_file}")
