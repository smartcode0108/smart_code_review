import subprocess
import os
import ollama

def run_pylint(file_path):
    """Runs Pylint and returns feedback."""
    pylint_output = subprocess.run(
        ['pylint', file_path],
        capture_output=True,
        text=True
    )
    return pylint_output.stdout

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
        - Fix all Pylint errors and warnings.
        - Provide ONLY the final, corrected Python code.
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
    """Processes a single file: runs Pylint, gets fixes, and applies them."""
    print(f"Processing file: {file_path}")
    pylint_feedback = run_pylint(file_path)
    print(f"Pylint Feedback for {file_path}:\n{pylint_feedback}")

    fixes = get_ollama_fixes(pylint_feedback, file_path)
    if fixes:
        print(f"Suggested Fixes for {file_path}:\n{fixes}")
        apply_ollama_fixes(file_path, fixes)
    else:
        print(f"No fixes suggested for {file_path}.")

def main():
    """Main function to process all changed Python files."""
    with open("changed_files.txt", "r") as file:
        changed_files = file.read().splitlines()

    for file_path in changed_files:
        if file_path.endswith(".py"):
            process_file(file_path)

if __name__ == "__main__":
    main()