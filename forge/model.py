import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def generate_tests(prompt: str, model_name: str) -> str:
    """
    Call the local LLM (via Ollama) to generate test code given the prompt.
    Returns the test code as a string.
    """
    # Prepare request payload for Ollama API
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stop": ["```"],       # stop at end of code block (if model outputs extra content)
        "stream": False        # get the full completion in one response
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Failed to generate tests via model: {e}")
    # Ollama returns NDJSON lines; with stream=False, should return a JSON with 'output' or similar
    data = response.json()
    # The exact key might be 'output' or 'response' depending on Ollama version; handle generically:
    test_code = data.get("output") or data.get("response") or ""
    if not test_code:
        # If not present, maybe the whole response text is the code
        test_code = response.text
    return test_code.strip()
