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
            return response  # Return the raw response object
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API request failed: {e}")

    def _handle_streaming_response(self, response):
        """
        Handle streaming response from Ollama API.
        """
        try:
            json_objects = []
            current_review = {"response": ""}  # To accumulate fragmented responses

            for line in response.iter_lines():
                if line:
                    try:
                        # Parse each line as a JSON object
                        json_object = json.loads(line.decode("utf-8"))
                        print(f"Received JSON object: {json_object}")  # Debugging

                        # Accumulate the response fragments
                        if "response" in json_object:
                            current_review["response"] += json_object["response"]

                        # If the review is complete (done is True), process it
                        if json_object.get("done", False):
                            # Add additional fields if they exist
                            current_review.update({
                                "line": json_object.get("line"),
                                "type": json_object.get("type"),
                                "severity": json_object.get("severity"),
                                "message": current_review["response"].strip()
                            })

                            # Only add valid reviews
                            if "line" in current_review and "message" in current_review:
                                json_objects.append(current_review)
                                print(f"Added valid review: {current_review}")  # Debugging

                            # Reset for the next review
                            current_review = {"response": ""}

                    except json.JSONDecodeError as e:
                        print(f"Skipping invalid JSON fragment: {line.decode('utf-8')}")
                        continue

            print(f"Final accumulated reviews: {json_objects}")  # Debugging
            return json_objects
        except Exception as e:
            print(f"Error processing streaming response from Ollama API: {e}")
            return []
        
    def review_code(self, content, filename, changed_lines):
        """
        Send code to the Ollama API for review and process the response.
        """
        if not self.should_review_file(filename):
            return []

        prompt = f"""
You are an expert code reviewer. Review the following code changes and provide specific, actionable feedback. Focus on:
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
3. Each line number must match one of: {changed_lines}
4. Consider context when making suggestions
5. Be specific and actionable in recommendations
6. For security issues, use the exact line where dangerous code appears
7. For other multi-line issues, use the first line number where the issue appears

If no issues found, return: []
"""

        
        response = self.make_request("/api/generate", {
            "model": self.model,
            "prompt": prompt,
            "stream": True,  # Ensure streaming is enabled
            "temperature": 0.1,
            "top_k": 10,
            "top_p": 0.9
        })

        # Check if the response is JSON or streaming
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            reviews = response.json().get("response", "[]")
            parsed_reviews = json.loads(reviews)
        else:
            parsed_reviews = self._handle_streaming_response(response)

        # Debugging: Print parsed reviews
        print(f"Parsed reviews: {parsed_reviews}")

        # Process reviews and provide default values for missing fields
        valid_reviews = []
        for review in parsed_reviews:
            review["line"] = review.get("line")  # Keep None for general comments
            review["type"] = review.get("type", "general")  # Default to "general"
            review["severity"] = review.get("severity", "low")  # Default to "low"
            review["message"] = review.get("message", "").strip()

            # Add the review to the valid list if it has a message
            if review["message"]:
                valid_reviews.append(review)

        print(f"Valid reviews: {valid_reviews}")
        return valid_reviews