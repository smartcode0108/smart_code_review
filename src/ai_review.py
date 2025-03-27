import os
import requests
import base64
from ollama import Ollama

# Initialize the Ollama model
AI_MODEL_NAME = "code-review"
ollama = Ollama(model="collama")

# GitHub environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

# Load the GitHub event payload
with open(GITHUB_EVENT_PATH, "r") as f:
    event = f.read()

# Parse the event payload
import json
event_data = json.loads(event)
pr_number = event_data["pull_request"]["number"]

# GitHub API headers
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# Step 1: Get the list of files in the PR
files_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{pr_number}/files"
response = requests.get(files_url, headers=headers)
response.raise_for_status()
files = response.json()

# Step 2: Analyze each file using Ollama
comments = []
for file in files:
    filename = file["filename"]
    raw_url = file["raw_url"]

    # Fetch the file content
    file_response = requests.get(raw_url, headers=headers)
    file_response.raise_for_status()
    code = file_response.text

    # Use Ollama to review the code
    prompt = f"Review the following code and suggest improvements:\n\n{code}"
    ai_response = ollama.generate(prompt=prompt)
    review_comment = ai_response.get("content", "No suggestions provided.")

    # Add a comment for this file
    comments.append({
        "path": filename,
        "position": 1,  # Comment on the first line of the file
        "body": review_comment,
    })

# Step 3: Post comments to the PR
comments_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{pr_number}/comments"
for comment in comments:
    response = requests.post(comments_url, headers=headers, json=comment)
    response.raise_for_status()