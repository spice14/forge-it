import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
from forge.modules.llm import generate_code_with_llm
from forge.utils import get_test_file_path, get_module_import_path, load_prompt

def extract_code_from_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_repo_tree(repo_root: str) -> str:
    tree = []
    for root, dirs, files in os.walk(repo_root):
        depth = root[len(repo_root):].count(os.sep)
        indent = '  ' * depth
        subdir = os.path.basename(root)
        tree.append(f"{indent}{subdir}/")
        for f in sorted(files):
            if not f.startswith(".") and f != "__pycache__":
                tree.append(f"{indent}  {f}")  # show filename with extension
    return "\n".join(tree)


def strip_markdown_fences(code: str) -> str:
    """Remove markdown fences and leading/explanatory lines."""
    # lines = code.splitlines()
    clean_lines = []
    for block in code.split("```"):
        # print(f"\n\nProcessing block: {block}")
        if block and not block.startswith("```") and "import p" in block:
            # print(f"\n\nAdding block: {block}")
            clean_lines.append(block.replace('python', ''))

    return "\n".join(clean_lines)

def strip_bad_imports(code: str) -> str:
    """Remove incorrect LLM-inserted import statements."""
    lines = code.splitlines()
    clean_lines = [
        line for line in lines
        if not line.strip().startswith("from module import")  # block LLM hallucinations
    ]
    return "\n".join(clean_lines).strip()

def generate_tests_for_file(file_path: str, repo_root: str):
    code = extract_code_from_file(file_path)
    if not code.strip():
        return

    # Skip test for init/setup-like files
    base_name = os.path.basename(file_path)
    if base_name in {"__init__.py", "setup.py"}:
        print(f"[INFO] Skipping {file_path}: not suitable for testing")
        return

    import_path = get_module_import_path(file_path, repo_root)
    test_lines = [f"import {import_path} as module", ""]

    prompt_template = load_prompt("base_prompt.txt")
    repo_tree = get_repo_tree(repo_root)

    print(repo_tree)

    file_rel_path = os.path.relpath(file_path, repo_root).replace("\\", "/")
    annotated_code = f"# Filename: {file_rel_path}\n\n{code}"
    prompt = prompt_template.replace("{code}", annotated_code).replace("{tree}", repo_tree)

    try:
        raw_output = generate_code_with_llm(prompt)
        
        cleaned_code = strip_markdown_fences(raw_output)
        cleaned_code = strip_bad_imports(cleaned_code)

        test_lines.append(cleaned_code)
    except Exception as e:
        print(f"[ERROR] Generating tests for '{file_path}' failed: {e}")
        return

    final_test_code = "\n".join(test_lines).rstrip() + "\n"
    test_file_path = get_test_file_path(file_path, repo_root)
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(final_test_code)

    print(f"[INFO] Wrote tests for '{file_path}' to '{test_file_path}'")

def process_repo(repo_path: str):
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d != '.git' and not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith(".py") and not file.startswith("test_"):
                file_path = os.path.join(root, file)
                generate_tests_for_file(file_path, repo_path)
