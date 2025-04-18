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
    **Docstring:**
    
    Summary:
    Determines if two comments are equal based on path, line number, and comment body.
    
    Args:
        existing (dict): Existing comment.
        new_comment (dict): New comment.
    
    Returns:
        bool: True if the comments are equal, False otherwise.
    """
    for existing in existing_comments:
        if (
            existing["path"] == new_comment["path"]
            and existing.get("line") == new_comment["line"]
            and new_comment["body"].strip() == existing.get("body", "").strip()
        ):
            return True
    return False


def get_changed_lines(hunk):
    """
    Summary line.
    
    Args:
        line (HunkLine): the line object.
    
    Returns:
        dict: context dictionary containing line content, type, and position.
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
    ## Summary
    
    Generates reviews for code changes in a GitHub pull request.
    
    ## Args:
    
    - `hunk` (dict): A dictionary containing information about the code changes in the pull request.
    
    ## Returns:
    
    - None
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
        comments_to_post = []
        general_comments = []

        existing_comments = github.get_existing_comments(
            GITHUB_REPOSITORY_OWNER, GITHUB_REPOSITORY.split("/")[1], PR_NUMBER
        )

        for review in reviews:
            if review.get("line") is not None:
                new_comment = {
                    "path": file.path,
                    "line": review["line"],
                    "side": "RIGHT",
                    "body": f"[{review['type'].upper()} - {review['severity'].capitalize()}] {review['message']}",
                }

                if not find_existing_comment(existing_comments, new_comment):
                    comments_to_post.append(new_comment)
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
            print(f"Posted review with inline comments")

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
        diff_output (str): Output of the `git diff` command.
    
    Returns:
        None
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
