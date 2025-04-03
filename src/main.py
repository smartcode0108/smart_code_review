import os
import json
import subprocess
from pathlib import Path
from fnmatch import fnmatch
import requests

# Constants and configuration
FILE_PATTERN = os.getenv("FILE_PATTERN", "*.ts")  # Default to TypeScript files
BASE_BRANCH = os.getenv("BASE_BRANCH", "origin/master")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_REPOSITORY_OWNER = os.getenv("GITHUB_REPOSITORY_OWNER")
PR_NUMBER = os.getenv("PR_NUMBER")
GITHUB_SHA = os.getenv("GITHUB_SHA")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

# Cache for existing comments
existing_comments_cache = None

# Function to get existing comments with caching
def get_existing_comments(owner, repo, pr_number):
    global existing_comments_cache
    if existing_comments_cache is None:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        existing_comments_cache = response.json()
    return existing_comments_cache

# Function to check if a similar comment already exists
def find_existing_comment(existing_comments, new_comment):
    for existing in existing_comments:
        if (
            existing["path"] == new_comment["path"]
            and existing["line"] == new_comment["line"]
            and new_comment["message"][:50] in existing["body"]
        ):
            return True
    return False

# Function to merge comments on the same line
def merge_comments(comments):
    merged_comments = {}
    for comment in comments:
        key = f"{comment['path']}:{comment['line']}"
        if key not in merged_comments:
            merged_comments[key] = {
                **comment,
                "body": f"💭 **{comment['type'].upper()}** ({comment['severity']})\n\n{comment['message']}",
            }
        else:
            merged_comments[key]["body"] += f"\n\n💭 **{comment['type'].upper()}** ({comment['severity']})\n\n{comment['message']}"
    return list(merged_comments.values())

# Function to get changed lines from a chunk
def get_changed_lines(chunk):
    changed_lines = {}
    added_lines = set()
    for change in chunk["changes"]:
        if change["type"] in ["add", "normal"]:
            line_num = change.get("ln") or change.get("ln2")
            if line_num:
                changed_lines[line_num] = {
                    "content": change["content"],
                    "type": change["type"],
                    "position": line_num,
                }
                if change["type"] == "add":
                    added_lines.add(line_num)
    return {"context": changed_lines, "added_lines": list(added_lines)}

# Function to process a chunk
def process_chunk(chunk, file, github, ollama):
    changed_lines = get_changed_lines(chunk)
    if not changed_lines["added_lines"]:
        return

    # Create a string with line numbers and content
    content_with_lines = "\n".join(
        f"{line_num}: {'[CHANGED]' if line['type'] == 'add' else ''} {line['content'].strip()}"
        for line_num, line in sorted(changed_lines["context"].items())
    )

    print(f"Reviewing {file['to']} with context:\n{content_with_lines}")
    print("Changed lines:", changed_lines["added_lines"])

    # Call Ollama API for review
    payload = {
        "model": "code-review",
        "prompt": f"Review the following code and suggest improvements:\n\n{content_with_lines}",
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(OLLAMA_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    reviews = response.json()

    comments_to_post = []
    for review in reviews:
        if review["line"] not in changed_lines["added_lines"]:
            print(f"Skipping review for invalid line number: {review['line']}")
            continue

        comments_to_post.append({
            "path": file["to"],
            "line": review["line"],
            "message": review["message"],
            "type": review.get("type", "info"),
            "severity": review.get("severity", "low"),
        })

    merged_comments = merge_comments(comments_to_post)
    existing_comments = get_existing_comments(GITHUB_REPOSITORY_OWNER, GITHUB_REPOSITORY.split("/")[1], PR_NUMBER)

    for comment in merged_comments:
        if find_existing_comment(existing_comments, comment):
            print(f"Skipping duplicate comment for {comment['path']}:{comment['line']}")
            continue

        print(f"Creating comment for {comment['path']} at line {comment['line']}")
        github.create_review_comment(
            GITHUB_REPOSITORY_OWNER,
            GITHUB_REPOSITORY.split("/")[1],
            PR_NUMBER,
            GITHUB_SHA,
            comment["path"],
            comment["line"],
            comment["body"],
        )

# Main function
def main():
    try:
        # Get the diff output
        diff_output = subprocess.check_output(["git", "diff", BASE_BRANCH, "HEAD"]).decode("utf-8")
        files = parse_diff(diff_output)

        # Filter files to review
        files_to_review = [file for file in files if fnmatch(file["to"], FILE_PATTERN)]
        print(f"Found {len(files)} changed files")
        print(f"Reviewing {len(files_to_review)} files matching pattern {FILE_PATTERN}")

        # Process chunks
        for file in files_to_review:
            for chunk in file["chunks"]:
                process_chunk(chunk, file, github, ollama)

        print("Code review completed successfully")
    except Exception as e:
        print(f"Error in code review process: {e}")
        exit(1)

if __name__ == "__main__":
    main()