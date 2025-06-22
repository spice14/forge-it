import os
import subprocess, json, sys
from pathlib import Path
from typing import Tuple

def get_test_file_path(src_path: str, repo_root: str) -> str:
    rel_path = os.path.relpath(src_path, repo_root)
    dir_name, file_name = os.path.split(rel_path)
    test_dir = os.path.join(repo_root, "tests", dir_name)
    os.makedirs(test_dir, exist_ok=True)
    test_file_name = f"test_{file_name}"
    return os.path.join(test_dir, test_file_name)

def get_module_import_path(src_path: str, repo_root: str) -> str:
    """
    Given a file path and the root of the repo, returns its import path.
    E.g., src_path=".../my_pkg/area.py" → "my_pkg.area"
    """
    rel_path = os.path.relpath(src_path, repo_root)
    no_ext = os.path.splitext(rel_path)[0]
    return no_ext.replace(os.sep, ".")

# ─── Agent-only helpers ─────────────────────────────────────────────
def run_tests_and_get_coverage(repo_root: str, timeout: int = 120) -> Tuple[float, str]:
    """Run `pytest --cov` and return (ratio, raw_output)."""
    repo = Path(repo_root)
    cov_json = repo / "coverage.json"
    cmd = [sys.executable, "-m", "pytest",
           "--cov=.", f"--cov-report=json:{cov_json}"]
    proc = subprocess.run(cmd, cwd=repo,
                          capture_output=True, text=True, timeout=timeout)
    output = proc.stdout + "\n" + proc.stderr
    if cov_json.exists():
        data = json.loads(cov_json.read_text())
        ratio = data["totals"]["percent_covered"] / 100.0
    else:
        ratio = 0.0
    return ratio, output

def get_directory_tree(root: Path) -> str:
    """
    Recreates the output of `tree /f /a` for a given directory.
    """
    output = []
    for path in sorted(root.rglob("*")):
        if "__pycache__" in path.parts or path.name.endswith(".pyc"):
            continue
        rel_path = path.relative_to(root)
        depth = len(rel_path.parts) - 1
        indent = "    " * depth
        if path.is_dir():
            output.append(f"{indent}{rel_path.name}/")
        else:
            output.append(f"{indent}{rel_path.name}")
    return "\n".join(output)
