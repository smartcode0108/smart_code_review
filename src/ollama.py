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
        return re.search(self.file_pattern, filename)

    def make_request(self, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API request failed: {e}")

    def _handle_streaming_response(self, response):
        code_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    json_object = json.loads(line.decode("utf-8"))
                    code_response += json_object["response"]
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON fragment: {line.decode('utf-8')}")
                    continue
        return code_response

    def review_code(self, content, filename, changed_lines):
        if not self.should_review_file(filename):
            return []

        # Fixed prompt to reduce echoing
        prompt = f"""You are an expert code reviewer. Review the code from file `{filename}`.
Only provide feedback for the following lines: {json.dumps(changed_lines)}.
Each line starts with its line number and a [CHANGED] tag if modified.

Focus on:
- Type safety
- Design patterns
- Readability and maintainability
- Security issues (use the exact line of risk)
- Performance

Example output:
[
  {{
    "line": 42,
    "type": "security",
    "severity": "high",
    "message": "Avoid using eval() due to security risks."
  }}
]

Code:
{content}
"""

        response = self.make_request("/api/generate", {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "temperature": 0.1,
            "top_k": 10,
            "top_p": 0.9
        })

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            reviews = response.json().get("response", "[]")
            parsed_reviews = json.loads(reviews)
        else:
            parsed_reviews = self._handle_streaming_response(response)

        print(f"Parsed reviews: {parsed_reviews}")

        valid_reviews = []
        for review in parsed_reviews:
            review["line"] = review.get("line")
            review["type"] = review.get("type", "general")
            review["severity"] = review.get("severity", "low")
            review["message"] = review.get("message", "").strip()

            if review["message"]:
                valid_reviews.append(review)

        print(f"Valid reviews: {valid_reviews}")
        return valid_reviews