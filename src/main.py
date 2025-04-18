import os
import subprocess
import requests
from unidiff import PatchSet
from github import GitHubAPI
from ollama import OllamaAPI

# Constants and configuration
BASE_BRANCH = os.getenv("BASE_BRANCH", "origin/master")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_REPOSITORY_OWNER = os.getenv("GITHUB_REPOSITORY_OWNER")
PR_NUMBER = os.getenv("PR_NUMBER")
GITHUB_SHA = os.getenv("GITHUB_SHA")


def find_existing_comment(existing_comments, new_comment):
    """
    Summary line.
    
    Args:
        existing (dict): description.
        new_comment (dict): description.
    
    Returns:
        bool: True if the comments are duplicates, False otherwise.
    """
    for existing in existing_comments:
        if (
            existing["path"] == new_comment["path"]
            and existing.get("line") == new_comment["line"]
            and new_comment["body"].strip() == existing.get("body", "").strip()
        ):
            return True
    return False


def deduplicate_reviews(reviews):
    """
    **Docstring:**
    
    Filters and removes duplicate reviews based on message, type, and severity, keeping only the latest review for each unique combination.
    
    Args:
        reviews (list): A list of dictionaries, each representing a review with keys "message", "type", "severity", and "line".
    
    Returns:
        list: A list of dictionaries representing the filtered reviews.
    """
    seen = set()
    filtered = []

    for review in sorted(reviews, key=lambda r: r["line"]):
        key = (review["message"].strip(), review["type"], review["severity"])
        if any(
            abs(review["line"] - other_line) <= 1 and key == other_key
            for other_key, other_line in seen
        ):
            continue
        filtered.append(review)
        seen.add((key, review["line"]))

    return filtered


def get_changed_lines(hunk):
    """
    Summary:
    Extracts added and context lines from a hunk object.
    
    Args:
        hunk (Hunk): The hunk object containing the lines.
    
    Returns:
        dict: A dictionary containing the context and added lines.
    """
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
    """
    Summary:
    Generates automated code reviews for pull requests using Ollama's code analysis capabilities.
    
    Args:
        hunk (dict): Git diff hunk containing code changes.
    
    Returns:
        None.
    """
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

        reviews = ollama.review_code(
            content=content_with_lines,
            filename=file.path,
            changed_lines=changed_lines["added_lines"],
        )
        print(f"Reviews returned by Ollama: {reviews}")
        reviews = deduplicate_reviews(reviews)
        print(f"Deduplicated reviews: {reviews}")
        comments_to_post = []
        general_comments = []

        existing_comments = github.get_existing_comments(
            GITHUB_REPOSITORY_OWNER, GITHUB_REPOSITORY.split("/")[1], PR_NUMBER
        )

        for review in reviews:
            if review.get("line") is not None:
                comment = {
                    "path": file.path,
                    "line": review["line"] + 1,
                    "side": "RIGHT",
                    "body": f"[{review['type'].upper()} - {review['severity'].capitalize()}] {review['message']}",
                }

                if not find_existing_comment(existing_comments, comment):
                    comments_to_post.append(comment)
                else:
                    print(f"Skipping duplicate comment on {file.path}:{review['line']}")
            else:
                general_comments.append(review["message"])

        if comments_to_post:
            github.create_review(
                GITHUB_REPOSITORY_OWNER,
                GITHUB_REPOSITORY.split("/")[1],
                PR_NUMBER,
                comments_to_post,
                body="Automated review by Ollama Code Review Bot",
            )
            print(f"Posted review with inline commenrs")

        if general_comments:
            body = "\n\n".join(general_comments)
            github.post_comment(
                GITHUB_REPOSITORY_OWNER,
                GITHUB_REPOSITORY.split("/")[1],
                PR_NUMBER,
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
    """
    Summary line.
    
    Args:
        github (GitHubAPI): GitHub API object.
        ollama (OllamaAPI): Ollama API object.
    
    Returns:
        None.
    """
    try:
        github = GitHubAPI(GITHUB_TOKEN)
        ollama = OllamaAPI()

        diff_output = subprocess.check_output(
            ["git", "diff", BASE_BRANCH, "HEAD"]
        ).decode("utf-8")
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
