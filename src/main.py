import os
import requests
from unidiff import PatchSet

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # Format: owner/repo
PR_NUMBER = os.getenv("PR_NUMBER")
COMMIT_SHA = os.getenv("COMMIT_SHA")

def load_patch(file_path='diff.patch'):
    print(f"[INFO] Loading patch file: {file_path}")
    with open(file_path) as f:
        patch = PatchSet(f)
    print("[INFO] Patch file loaded successfully.")
    return patch

def post_inline_comment(file_path, line_number, body):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}/comments"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {
        "body": body,
        "commit_id": COMMIT_SHA,
        "path": file_path,
        "side": "RIGHT",
        "line": line_number
    }

    print(f"[INFO] Posting comment to {file_path}:{line_number}")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 201:
        print(f"[ERROR] Failed to post comment: {response.status_code} - {response.text}")
    else:
        print("[INFO] Comment posted successfully.")