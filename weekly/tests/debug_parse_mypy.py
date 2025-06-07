"""Debug script for testing mypy output parsing."""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from weekly.checkers.style import StyleChecker

def test_parse_mypy_output():
    """Test parsing mypy output."""
    output = """
    /path/to/file.py:10: error: Incompatible return value type (got "int", expected "str")  [return-value]
    /path/to/file.py: note: In function "example"
    /path/to/file.py:5: note: Called from here
    /path/to/file.py:10: note: Revealed type is "builtins.int"
    /path/to/file.py:10: note: "return" has type "int"; expected "str"
    Found 1 error in 1 file (checked 1 source file)
    """
    
    style_checker = StyleChecker()
    style_checker._parse_mypy_output(output)
    
    print(f"Issues found: {len(style_checker.issues)}")
    for i, issue in enumerate(style_checker.issues, 1):
        print(f"\nIssue {i}:")
        print(f"  Tool: {issue.tool}")
        print(f"  File: {issue.file_path}")
        print(f"  Line: {issue.line}")
        print(f"  Column: {issue.column}")
        print(f"  Code: {issue.code}")
        print(f"  Message: {issue.message}")

if __name__ == "__main__":
    test_parse_mypy_output()
