import json
import requests
import re
from fnmatch import fnmatch
from config import REVIEW_CONFIG


class OllamaAPI:
    def __init__(self, model="codellama"):
        self.base_url = "http://127.0.0.1:11434"
        self.model = model
        self.file_pattern = REVIEW_CONFIG.get("supportedExtensions", "**/*.{ts,tsx}")

    def should_review_file(self, filename):
        """
        Check if the file matches the supported file pattern.
        """
        return re.search(self.file_pattern, filename)

    def make_request(self, endpoint, data):
        """
        Make a POST request to the Ollama API.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API request failed: {e}")

    def review_code(self, content, filename, changed_lines):
        """
        Send code to the Ollama API for review and process the response.
        """
        if not self.should_review_file(filename):
            return []

        prompt = f"""You are an expert code reviewer. Review the following code changes and provide specific, actionable feedback. Focus on:
1. Type safety and potential runtime issues
2. Architecture and design patterns
3. Code readability and maintainability
4. Security vulnerabilities (IMPORTANT: for security issues like 'eval', use the EXACT line where the dangerous function is called)
5. Performance implications

The code below shows:
- Each line starts with its EXACT line number followed by a colon
- Changed lines are marked with [CHANGED]
- You MUST use the EXACT line number shown at the start of the line in your response
- DO NOT use a line number unless you see it explicitly at the start of a line
- For security issues, use the line number where the actual dangerous code appears
- For other multi-line issues, use the first line number where the issue appears
- Context lines are shown without markers

IMPORTANT NOTES:
- For security issues (like eval, Function constructor, etc.), always use the line number where the dangerous function is actually called
- For performance issues (like nested loops), use the line number of the outer function or loop
- Double-check that your line numbers match exactly with where the issue occurs

Code to review from {filename}:

{content}

Response format (use EXACT line numbers from the start of lines):
[
  {{
    "line": <number_from_start_of_line>,
    "type": "type-safety" | "architecture" | "readability" | "security" | "performance" | "suggestion" | "good-practice",
    "severity": "high" | "medium" | "low",
    "message": "<specific_issue_and_recommendation>"
  }}
]

Rules:
1. Only comment on [CHANGED] lines
2. Use EXACT line numbers shown at start of lines
3. Each line number must match one of: {json.dumps(changed_lines)}
4. Consider context when making suggestions
5. Be specific and actionable in recommendations
6. For security issues, use the exact line where dangerous code appears
7. For other multi-line issues, use the first line number where the issue appears

If no issues found, return: []"""

        try:
            response = self.make_request("/api/generate", {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
                "top_k": 10,
                "top_p": 0.9
            })

            try:
                reviews = json.loads(response.get("response", "[]"))
                return [
                    review for review in reviews
                    if review.get("line") in changed_lines and
                    review.get("type") and
                    review.get("severity") and
                    review.get("message")
                ]
            except json.JSONDecodeError as error:
                print("Error parsing Ollama review response:", error)
                return []
        except Exception as error:
            print("Error during code review:", error)
            return []