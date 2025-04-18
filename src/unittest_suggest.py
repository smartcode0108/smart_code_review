import ast
import os
import sys
import subprocess
import requests
from unidiff import PatchSet
from github import GitHubAPI
from main import get_changed_lines


class OllamaAPI:
    def __init__(self, model="codegemma:7b-instruct"):
        self.base_url = "http://127.0.0.1:11434"
        self.model = model

    def suggest_unittest(self, code_snippet):
        prompt = f"""Generate a Python unittest (using unittest module) for the following function.
Just output the test function code only. No explanations or markdown.

Function:
{code_snippet}
"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        response_json = response.json()
        if "response" not in response_json:
            raise KeyError(f"'response' key not found in API response: {response_json}")
        return response_json["response"].strip()


def extract_new_functions(file_path, changed_lines, is_new_file=False):
    """
    ## Function Docstring
    
    
    Summary:
       Identifies newly added or modified functions in a source code file.
    
    Args:
       file_path (str): Path to the source code file.
       is_new_file (bool): Whether the file is newly created.
       changed_lines (list): List of line numbers that have been modified.
    
    Returns:
       list: List of newly or modified functions in the file.
    """
    new_funcs = []
    with open(file_path, "r") as f:
        source_code = f.read()
        tree = ast.parse(source_code)

    for node in ast.walk(tree):
        """
        Summary line.
        
        Returns:
            type: description.
        """
        if isinstance(node, ast.FunctionDef):
            if is_new_file or node.lineno in changed_lines:
                new_funcs.append(node)
    return new_funcs

def is_new_file(file_path):
    """
    **Docstring:**
    
    Summary:
    Checks if a specific file has been added (status 'A') compared to the remote origin/master branch.
    
    Args:
        file_path (str): The path to the file.
    
    Returns:
        bool: True if the file is new, False otherwise.
    """
    try:
        result = subprocess.check_output(
            ["git", "diff", "--name-status", "origin/master", file_path]
        ).decode("utf-8")
        for line in result.splitlines():
            status, path = line.split("\t")
            if path == file_path and status == "A":
                return True
    except subprocess.CalledProcessError as e:
        print(f"Error checking if file is new: {e}")
    return False


def format_test_comment(file_path, test_suggestions):
    """
    Summary line.
    Args:
        func_name (str): Name of the function.
        test_code (str): Test code for the function.
    Returns:
        str: HTML comment body with suggestions.
    """
    comment_body = f"### Unit Test Suggestions for `{file_path}`\n\n"
    comment_body += "<details><summary>Show Suggestions</summary>\n\n"

    for func_name, test_code in test_suggestions.items():
        if not test_code.strip():
            continue

        # Remove any internal markdown fences from generated code
        clean_test_code = test_code.replace("```python", "").replace("```", "").strip()

        comment_body += f"#### `{func_name}`\n\n"
        comment_body += "```python\n"
        comment_body += clean_test_code + "\n"
        comment_body += "```\n\n"

    comment_body += "</details>"
    return comment_body


def main():
    """
    Summary line.
    
    Args:
        file_path (str): description.
    
    Returns:
        None
    """
    if len(sys.argv) < 2:
        print("Usage: python unittest_suggest.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    print(f"Processing file: {file_path}")

    is_new = is_new_file(file_path)
    if is_new:
        print(f"{file_path} is a new file. Processing all functions.")
        changed_lines = list(range(1, len(open(file_path).readlines()) + 1))
    else:
        diff_output = subprocess.check_output(
            ["git", "diff", "origin/master", file_path]
        ).decode("utf-8")
        patch = PatchSet(diff_output)
        changed_lines = []
        for hunk in patch[0]:
            hunk_lines = get_changed_lines(hunk)
            changed_lines.extend(hunk_lines["added_lines"])

    if len(changed_lines) > 100 and not is_new:
        print(f"Too many changed lines in {file_path}. Skipping.")
        return

    new_funcs = extract_new_functions(file_path, changed_lines, is_new_file=is_new)
    if not new_funcs:
        print(f"No new functions in changed lines for {file_path}. Skipping.")
        return

    ollama = OllamaAPI()
    test_suggestions = {}

    with open(file_path) as f:
        source = f.read()

    for func in new_funcs:
        code_snippet = ast.get_source_segment(source, func)
        if not code_snippet:
            continue
        print(f"Generating test for `{func.name}`...")
        try:
            suggestion = ollama.suggest_unittest(code_snippet)
            test_suggestions[func.name] = suggestion
        except Exception as e:
            print(f"Failed to generate test for `{func.name}`: {e}")

    if not test_suggestions:
        print("No valid suggestions to post.")
        return

    comment_body = format_test_comment(file_path, test_suggestions)

    github_token = os.getenv("GITHUB_TOKEN")
    pr_number = os.getenv("PR_NUMBER")
    repo_owner = os.getenv("GITHUB_REPOSITORY_OWNER")
    repo_name = os.getenv("GITHUB_REPOSITORY").split("/")[-1]

    if not all([github_token, pr_number, repo_owner, repo_name]):
        print("Missing required environment variables for posting a comment.")
        return

    github_api = GitHubAPI(github_token)
    github_api.genaral_comment_to_pr(
        repo_owner, repo_name, int(pr_number), comment_body
    )


if __name__ == "__main__":
    main()
