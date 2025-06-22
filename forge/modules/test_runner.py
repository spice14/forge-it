# file: forge/modules/test_runner.py

import subprocess
import os

def run_pytest(repo_path: str, coverage: bool = False):
    """
    Run pytest on the repo. Add repo_path to PYTHONPATH so tests can import local modules.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = repo_path + os.pathsep + env.get("PYTHONPATH", "")

    cmd = ["pytest"]
    if coverage:
        cmd += ["--cov", repo_path]

    try:
        subprocess.run(cmd, cwd=repo_path, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Pytest exited with code {e.returncode}")
