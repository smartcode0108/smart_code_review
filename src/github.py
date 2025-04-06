import logging
import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")


def post_inline_comment(owner, repo, pull_number, commit_id, path, position, body):
    logging.debug(f"Posting inline comment on {path} at line {position}")
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pull_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "position": position,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        logging.error(f"Failed to post inline comment: {response.text}")
    return response.json()


def post_general_comment(owner, repo, issue_number, body):
    logging.debug("Posting general comment")
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {"body": body}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        logging.error(f"Failed to post general comment: {response.text}")
    return response.json()