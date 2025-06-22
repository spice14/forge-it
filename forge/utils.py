import os

def get_test_file_path(file_path: str, repo_root: str) -> str:
    relative_path = os.path.relpath(file_path, repo_root)
    module_name = os.path.splitext(os.path.basename(relative_path))[0]
    tests_dir = os.path.join(repo_root, "tests")
    os.makedirs(tests_dir, exist_ok=True)
    return os.path.join(tests_dir, f"test_{module_name}.py")


def get_module_import_path(src_path: str, repo_root: str) -> str:
    """
    Given a file path and the root of the repo, returns its import path.
    E.g., src_path=".../my_pkg/area.py" → "my_pkg.area"
    """
    rel_path = os.path.relpath(src_path, repo_root)
    no_ext = os.path.splitext(rel_path)[0]
    return no_ext.replace(os.sep, ".")

def load_prompt(name: str) -> str:
    prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")  # fix here
    path = os.path.normpath(os.path.join(prompts_dir, name))
    if not os.path.exists(path):
        raise FileNotFoundError(f"[load_prompt] Prompt file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
