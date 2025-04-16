from enum import Enum
import subprocess
import os
from ollama import OllamaAPI
from unidiff import PatchSet
import json

BASE_BRANCH = os.getenv("BASE_BRANCH", "origin/master")


class ResponseFormat(Enum):
    JSON = "json_object"
    TEXT = "text"


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


def run_pylint_on_changed_lines(file_path, changed_lines):
    """Run Pylint on the changed lines of a file."""
    pylint_output = subprocess.run(
        ["pylint", file_path], capture_output=True, text=True
    ).stdout
    print(f"Full Pylint output for {file_path}:\n{pylint_output}")  # Debugging log
    # Filter Pylint output to include only issues in the changed lines
    filtered_output = []
    for line in pylint_output.splitlines():
        if any(f"{file_path}:{line_num}:" in line for line_num in changed_lines):
            filtered_output.append(line)
    return "\n".join(filtered_output)


def generate_ollama_fix_prompt(pylint_feedback, file_path):
    """Generates a prompt for Ollama to suggest fixes based on Pylint feedback."""
    try:
        with open(file_path, "r") as file:
            code = file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

    prompt = f"""
    Given the following Pylint feedback, analyze the code and provide the final, fully corrected code.

    Pylint Feedback:
    {pylint_feedback}

    Python Code:
    {code}

    Your task is to:
       - Shorten overly long function names.
       - Make variable names more descriptive.
       - Add docstrings where necessary.
       - Add checks to prevent out-of-range indexing.

    """
    return prompt


def get_ollama_fixes(ollama, pylint_feedback, file_path):
    """Use Ollama to get code fixes based on Pylint feedback."""
    prompt = generate_ollama_fix_prompt(pylint_feedback, file_path)
    response = ollama.make_request(
        "/api/generate",
        {
            "model": "codellama",
            "prompt": prompt,
            "stream": True,
            "temperature": 0.1,
            "top_k": 10,
            "top_p": 0.9,
        },
    )

    # Print the raw response for debugging
    concatenated_response = ollama._handle_streaming_response(response)

    # Print the concatenated response for debugging
    print(f"Concatenated Ollama Response for {file_path}:\n{concatenated_response}")

    # Attempt to parse the concatenated response as JSON
    try:
        response_data = json.loads(concatenated_response)
        if isinstance(response_data, dict) and "response" in response_data:
            fixed_code = response_data["response"]
        else:
            print(f"Unexpected response format for {file_path}: {response_data}")
            return None
    except json.JSONDecodeError:
        # If JSON decoding fails, assume the response is plain text with code
        print(f"JSON decoding failed for {file_path}. Using raw response as fixes.")
        fixed_code = concatenated_response.strip()

    # Extract Python code from the response
    if "```python" in fixed_code:
        fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
    elif "```" in fixed_code:
        fixed_code = fixed_code.split("```")[1].split("```")[0].strip()

    return fixed_code


def apply_ollama_fixes(file_path, fixes):
    """Applies the suggested fixes to the file."""
    if not fixes or not fixes.strip():
        print(f"No valid fixes provided for {file_path}. Skipping file.")
        return

    try:
        print(f"Writing fixes to {file_path}:\n{fixes}")  # Debugging log
        with open(file_path, "a") as file:
            file.write(fixes)
        print(f"Fixes successfully applied to {file_path}.")
    except Exception as e:
        print(f"Error writing fixes to {file_path}: {e}")


def process_file(ollama, hunk, file_path):
    """Process a single file: run Pylint on changed lines and apply fixes."""
    print(f"Processing hunk in file: {file_path}")
    changed_lines = get_changed_lines(hunk)
    if not changed_lines:
        print(f"No changes detected in {file_path}. Skipping Pylint.")
        return

    pylint_feedback = run_pylint_on_changed_lines(
        file_path, changed_lines["added_lines"]
    )
    print(f"Pylint Feedback for {file_path}:\n{pylint_feedback}")

    if pylint_feedback:
        print(f"Pylint issues detected in {file_path}:\n{pylint_feedback}")
        fixes = get_ollama_fixes(ollama, pylint_feedback, file_path)
        if fixes:
            print(f"Ollama suggested fixes for {file_path}:\n{fixes}")
            apply_ollama_fixes(file_path, fixes)
        else:
            print(f"No valid fixes suggested by Ollama for {file_path}.")
    else:
        print(f"No Pylint issues detected in {file_path}.")


def main():
    """Main function to process all changed Python files."""
    ollama = OllamaAPI()
    diff_output = subprocess.check_output(["git", "diff", BASE_BRANCH, "HEAD"]).decode(
        "utf-8"
    )
    changed_files = PatchSet(diff_output)
    print(f"Found {len(changed_files)} changed files")

    for patched_file in changed_files:
        file_path = patched_file.path
        if not file_path.endswith(
            ".py"
        ):  # Extract the file path from the PatchedFile object
            print(f"Processing file: {file_path}")
            continue

        for hunk in patched_file:
            process_file(ollama, hunk, file_path)


if __name__ == "__main__":
    main()
