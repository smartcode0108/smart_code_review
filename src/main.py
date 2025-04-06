import base64
import json
import logging
import os
from flask import Flask, request, jsonify

from github import post_general_comment, post_inline_comment
from ollama import review_code

app = Flask(__name__)


def extract_diff_from_payload(payload):
    logging.debug("Extracting diffs from payload")
    files = payload.get("pull_request", {}).get("files", [])
    diffs = []
    for f in files:
        patch = f.get("patch")
        filename = f.get("filename")
        if patch and filename:
            diff_block = f"diff --git a/{filename} b/{filename}\n{patch}"
            diffs.append(diff_block)
    logging.debug(f"Extracted {len(diffs)} diff blocks")
    return "\n".join(diffs)


@app.route("/review", methods=["POST"])
def review():
    logging.debug("/review endpoint called")
    try:
        payload = request.get_json()
    except Exception as e:
        logging.error(f"Invalid JSON payload: {e}")
        return jsonify({"error": "Invalid JSON"}), 400

    if not payload:
        logging.error("No payload received")
        return jsonify({"error": "Missing payload"}), 400

    event_type = request.headers.get("X-GitHub-Event")
    logging.debug(f"Received GitHub event: {event_type}")
    if event_type != "pull_request":
        return jsonify({"message": "Event ignored"}), 200

    action = payload.get("action")
    logging.debug(f"PR action: {action}")
    if action not in ["opened", "synchronize"]:
        return jsonify({"message": "Action ignored"}), 200

    pull_request = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    owner = repo.get("owner", {}).get("login")
    repo_name = repo.get("name")
    pull_number = pull_request.get("number")
    head = pull_request.get("head", {})
    commit_id = head.get("sha")

    logging.debug(f"Reviewing PR #{pull_number} in repo {owner}/{repo_name}")
    diff_text = extract_diff_from_payload(payload)
    if not diff_text:
        logging.warning("No diff found in payload")
        return jsonify({"message": "No diff to review"}), 200

    try:
        review_result = review_code(diff_text)
        logging.debug(f"Raw review result: {review_result[:500]}")

        if not review_result:
            logging.warning("No review content returned from Ollama")
            return jsonify({"message": "Review content empty"}), 200

        try:
            review_json = json.loads(review_result)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode review JSON: {e}\nReview text was:\n{review_result}")
            return jsonify({"error": "Invalid review format"}), 500

        comments = review_json.get("comments", [])
        comments = [c for c in comments if c.get("file") and c.get("line") and c.get("comment")]
        logging.debug(f"Filtered {len(comments)} valid inline comments")

        if not comments and not review_json.get("general_comment"):
            logging.warning("Filtered out all hallucinated comments, nothing to post")
            return jsonify({"message": "No useful review comments found"}), 200

        for comment in comments:
            logging.debug(f"Posting comment on {comment['file']}:{comment['line']}")
            post_inline_comment(owner, repo_name, pull_number, commit_id, comment.get("file"), comment.get("line"), comment.get("comment"))

        general_comment = review_json.get("general_comment")
        if general_comment:
            logging.debug("Posting general comment")
            post_general_comment(owner, repo_name, pull_number, general_comment)

        return jsonify({"message": "Review posted"}), 200
    except Exception as e:
        logging.error(f"Review processing failed: {e}")
        return jsonify({"error": "Processing failed"}), 500


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))