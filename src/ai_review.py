import os
import requests
import json

# GitHub environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

# Ollama API details
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Local Ollama API endpoint
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")  # Store your API key in GitHub Secrets (if required)

# Load the GitHub event payload
with open(GITHUB_EVENT_PATH, "r") as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]

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

# Step 2: Analyze each file using the Ollama API
comments = []
for file in files:
    filename = file["filename"]
    raw_url = file["raw_url"]

    # Fetch the file content
    file_response = requests.get(raw_url, headers=headers)
    file_response.raise_for_status()
    code = file_response.text

    # Use the Ollama API to review the code
    payload = {
        "model": "code-review",  # Replace with the appropriate model name
        "prompt": f"Review the following code and suggest improvements:\n\n{code}",
    }
    api_headers = {
        "Content-Type": "application/json",
    }
    if OLLAMA_API_KEY:  # Add API key if required
        api_headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"

    api_response = requests.post(OLLAMA_API_URL, headers=api_headers, json=payload)
    api_response.raise_for_status()
    review_comment = api_response.json().get("content", "No suggestions provided.")

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