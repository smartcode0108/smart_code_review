import subprocess
import os
import ollama

def get_changed_lines(file_path):
    """Get the changed lines in a file using git diff."""
    diff_output = subprocess.run(
        ['git', 'diff', '-U0', file_path],
        capture_output=True,
        text=True
    ).stdout

    changed_lines = []
    for line in diff_output.splitlines():
        if line.startswith('@@'):
            # Extract line range from diff hunk header (e.g., @@ -1,2 +3,4 @@)
            parts = line.split(' ')
            added_lines = parts[2]  # e.g., "+3,4"
            start_line, line_count = map(int, added_lines[1:].split(',')) if ',' in added_lines else (int(added_lines[1:]), 1)
            changed_lines.extend(range(start_line, start_line + line_count))

    return changed_lines

def run_pylint_on_changed_lines(file_path, changed_lines):
    """Run Pylint on the changed lines of a file."""
    pylint_output = subprocess.run(
        ['pylint', file_path],
        capture_output=True,
        text=True
    ).stdout

    # Filter Pylint output to include only issues in the changed lines
    filtered_output = []
    for line in pylint_output.splitlines():
        if any(f"{file_path}:{line_num}:" in line for line_num in changed_lines):
            filtered_output.append(line)

    return '\n'.join(filtered_output)
def generate_ollama_fix_prompt(pylint_feedback, file_path):
    """Generates a prompt for Ollama to suggest fixes based on Pylint feedback."""
    try:
        with open(file_path, 'r') as file:
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

def get_ollama_fixes(pylint_feedback, file_path):
    """Use Ollama to get code fixes based on Pylint feedback."""
    prompt = generate_ollama_fix_prompt(pylint_feedback, file_path)
    response = ollama.generate(
        model="codellama",
        prompt=prompt,
        options={"temperature": 0},
    )
    print(f"Ollama Response for {file_path}:\n{response.get('response', '')}")
    return response.get("response", "")

def apply_ollama_fixes(file_path, fixes):
    """Applies the suggested fixes to the file."""
    if not fixes.strip():
        print(f"No fixes provided for {file_path}.")
        return

    with open(file_path, 'w') as file:
        file.write(fixes)
    print(f"Fixes applied to {file_path}.")

def process_file(file_path):
    """Process a single file: run Pylint on changed lines and apply fixes."""
    print(f"Processing file: {file_path}")
    changed_lines = get_changed_lines(file_path)
    if not changed_lines:
        print(f"No changes detected in {file_path}. Skipping Pylint.")
        return

    pylint_feedback = run_pylint_on_changed_lines(file_path, changed_lines)
    print(f"Pylint Feedback for {file_path}:\n{pylint_feedback}")

    # Here you can integrate Ollama to fix the issues if needed
    # For now, just print the feedback
    if pylint_feedback:
        print(f"Pylint issues detected in {file_path}:\n{pylint_feedback}")
    else:
        print(f"No Pylint issues detected in {file_path}.")

def main():
    """Main function to process all changed Python files."""
    with open("changed_files.txt", "r") as file:
        changed_files = file.read().splitlines()

    for file_path in changed_files:
        if file_path.endswith(".py"):
            process_file(file_path)

if __name__ == "__main__":
    main()