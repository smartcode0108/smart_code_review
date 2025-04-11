import os
import json
import subprocess
from pathlib import Path
import requests
from unidiff import PatchSet
from stats import ReviewStats
from github import GitHubAPI
from ollama import OllamaAPI

# Constants and configuration
BASE_BRANCH = os.getenv("BASE_BRANCH", "origin/master")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_REPOSITORY_OWNER = os.getenv("GITHUB_REPOSITORY_OWNER")
PR_NUMBER = os.getenv("PR_NUMBER")
GITHUB_SHA = os.getenv("GITHUB_SHA")

existing_comments_cache = None

def get_existing_comments(owner, repo, pr_number):
    global existing_comments_cache
    if existing_comments_cache is None:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        existing_comments_cache = response.json()
    return existing_comments_cache

def find_existing_comment(existing_comments, new_comment):
    for existing in existing_comments:
        if (
            existing["path"] == new_comment["path"]
            and existing["line"] == new_comment["line"]
            and new_comment["message"][:50] in existing["body"]
        ):
            return True
    return False

def merge_comments(comments):
    merged_comments = {}
    for comment in comments:
        key = f"{comment['path']}:{comment['line']}"
        if key not in merged_comments:
            merged_comments[key] = {
                **comment,
                "body": f":thought_balloon: **{comment['type'].upper()}** ({comment['severity']})\n\n{comment['message']}",
            }
        else:
            merged_comments[key]["body"] += f"\n\n:thought_balloon: **{comment['type'].upper()}** ({comment['severity']})\n\n{comment['message']}"
    return list(merged_comments.values())

def get_changed_lines(hunk):
    changed_lines = {}
    added_lines = set()

    for line in hunk:
        if line.is_added or line.is_context:
            line_num = line.target_line_no
            if line_num:
                changed_lines[line_num] = {
                    "content": line.value,
                    "type": "add" if line.is_added else "normal",
                    "position": line_num,
                }
                if line.is_added:
                    added_lines.add(line_num)

    return {"context": changed_lines, "added_lines": list(added_lines)}

def process_chunk(hunk, file, github, ollama):
    try:
        changed_lines = get_changed_lines(hunk)
        if not changed_lines:
            return

        content_with_lines = "\n".join(
            f"{line_num}: {'[CHANGED]' if line['type'] == 'add' else ''} {line['content'].strip()}"
            for line_num, line in sorted(changed_lines["context"].items())
        )
        print(f"Reviewing {file.path} with context:\n{content_with_lines}")
        print("changed_lines", changed_lines["added_lines"])

        reviews = ollama.review_code(content=content_with_lines, filename=file.path, changed_lines=changed_lines["added_lines"])
        print(f"Reviews returned by Ollama: {reviews}")
        comments_to_post = []
        general_comments = []

        for review in reviews:
            if review.get("line") is not None and review.get("path"):
                comments_to_post.append({
                    "path": file.path,
                    "line": review["line"],
                    "body": f"{review['message']}"
                })
            else:
                general_comments.append(review["message"])

        for comment in comments_to_post:
            github.create_review_comment(
                GITHUB_REPOSITORY_OWNER,
                GITHUB_REPOSITORY.split("/")[1],
                PR_NUMBER,
                GITHUB_SHA,
                comment["path"],
                comment["line"],
                comment["body"],
            )
            print(f"Posted comment for {comment['path']} at line {comment['line']}")

        if general_comments:
            body = "\n\n".join(general_comments)
            github.create_review_comment(
                GITHUB_REPOSITORY_OWNER,
                GITHUB_REPOSITORY.split("/")[1],
                PR_NUMBER,
                GITHUB_SHA,
                None,
                None,
                body,
            )
            print("Posted general comments to the pull request.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return
    except Exception as err:
        print(f"An error occurred: {err}")
        return

def main():
    try:
        github = GitHubAPI(GITHUB_TOKEN)
        ollama = OllamaAPI()

        diff_output = subprocess.check_output(["git", "diff", BASE_BRANCH, "HEAD"]).decode("utf-8")
        files = PatchSet(diff_output)

        print(f"Found {len(files)} changed files")
        for file in files:
            for hunk in file:
                process_chunk(hunk, file, github, ollama)

        print("Code review completed successfully")
    except Exception as e:
        print(f"Error in code review process: {e}")
        exit(1)

if __name__ == "__main__":
    main()