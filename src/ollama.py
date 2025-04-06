import logging
import os
import requests

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

REVIEW_PROMPT_TEMPLATE = """
You are a senior software engineer helping review code diffs.
Analyze the following unified diff and provide constructive feedback:
- Suggest improvements
- Point out potential bugs
- Recommend best practices
Return the response in JSON format with this structure:
{
  "comments": [
    {"file": "filename.py", "line": 10, "comment": "Comment text"},
    ...
  ],
  "general_comment": "Overall review comment."
}
Diff:
{diff}
"""

def review_code(diff):
    logging.debug("Preparing prompt for Ollama")
    prompt = REVIEW_PROMPT_TEMPLATE.format(diff=diff)
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        logging.debug("Sending request to Ollama")
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        json_data = response.json()
        logging.debug("Received response from Ollama")
        return json_data.get("response", "")
    except requests.RequestException as e:
        logging.error(f"Failed to contact Ollama API: {e}")
        return ""
    except ValueError as e:
        logging.error(f"Invalid response from Ollama API: {e}")
        return ""