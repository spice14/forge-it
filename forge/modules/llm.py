import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# file: forge/modules/llm.py

import requests
from pathlib import Path
from forge.modules.utils import get_directory_tree  # Add at top

_PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
_BASE       = _PROMPT_DIR / "base_prompt.txt"
_REFINE     = _PROMPT_DIR / "refinement_prompt.txt"
OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_code_with_llm(prompt: str, model: str = "codellama:7b") -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": True},
            stream=True,
            timeout=60
        )
        response.raise_for_status()

        # Collect the full output from streamed chunks
        output = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = line.decode("utf-8")
                    # parse line as JSON
                    import json
                    data = json.loads(chunk)
                    output += data.get("response", "")
                except Exception as e:
                    print(f"[WARN] Could not decode line: {e}")
        return output.strip()

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ollama API request failed: {e}")

# ─── Agent-aware prompt wrappers ────────────────────────────────────

def _fill(template: Path, **kw): return template.read_text(encoding="utf-8").format(**kw)

def generate_initial_test(*, source_code, module_import_path, func_names,
                          repo_root: Path,
                          model="codellama:7b") -> str:
    tree = get_directory_tree(repo_root)
    prompt = _fill(_BASE,
                   code=source_code,
                   module=module_import_path,
                   functions=", ".join(func_names),
                   tree=tree)
    return generate_code_with_llm(prompt, model)


def generate_refined_test(*, original_test, pytest_output, source_code,
                          model="codellama:7b") -> str:
    prompt = _fill(_REFINE,
                   existing_tests=original_test,
                   pytest_output=pytest_output,
                   code=source_code)
    return generate_code_with_llm(prompt, model)
