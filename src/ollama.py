import json
import requests
import re


# Import config
from config import REVIEW_CONFIG

class OllamaAPI:
    def __init__(self, model="codellama"):
        self.base_url = "http://127.0.0.1:11434"
        self.model = model
        self.file_pattern = REVIEW_CONFIG.get("supportedExtensions", "**/*.{ts,tsx}")

    def should_review_file(self, filename):
        return bool(re.search(self.file_pattern, filename))

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
        code_response = []
        for line in response.iter_lines():
            if not line:
                continue
            try:
                json_object = json.loads(line.decode("utf-8"))
                code_response.append(json_object.get("response", ""))
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON fragment: {line.decode('utf-8')}")
                continue

        # Join the responses into a single string
        concatenated_response = "".join(code_response)

        # Handle empty or malformed concatenated response
        if not concatenated_response.strip():
            print("No valid response received from Ollama.")
            return ""

        return concatenated_response

    def review_code(self, content, filename, changed_lines):
        if not self.should_review_file(filename):
            print(f"Skipping review for unsupported file type: {filename}")
            return []

        # Fixed prompt to reduce echoing
        prompt_template = REVIEW_CONFIG["reviewPrompt"]
        prompt = prompt_template.format(
            filename=filename,
            changed_lines=json.dumps(changed_lines),
            content=content
            )
        print("Prompt sent to ollama:\n", prompt)

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
            try:
                parsed_reviews = json.loads(reviews)
            except json.JSONDecodeError:
                print("Failed to parse JSON response")
                parsed_reviews = []
        else:
            parsed_response = self._handle_streaming_response(response)
            try:
                parsed_reviews = json.loads(parsed_response)
            except json.JSONDecodeError:
                print("Failed to parse streamed response")
                parsed_reviews = []


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