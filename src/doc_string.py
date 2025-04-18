import ast
import requests
import sys
import difflib


class OllamaAPI:
    def __init__(self, model="codegemma:7b-instruct"):
        """
        Summary: Initializes the model for the user.

        Args:
            model (object): The model object.

        Returns:
            None
        """
        self.base_url = "http://127.0.0.1:11434"
        self.model = model

    def generate_docstring(self, code_snippet):
        """
        Generates a Python docstring for the given function code snippet.

        Args:
            code_snippet (str): The source code of the function for which the docstring is to be generated.

        Returns:
            str: The generated docstring content, formatted as plain text without any Python code or markdown.
        """
        prompt = f"""You are a docstring generator.
                Your job is to generate ONLY the Python docstring content for the function below. 
                DO NOT include the function definition or any Python code in the output.
                DO NOT include:
                - Any lines starting with 'def', 'return', or function logic
                - Triple quotes or markdown formatting (e.g., ```python)
                - Notes, examples, explanations, or indentation
                ONLY return the raw docstring content like:
                Summary line.
                Args:
                    param1 (type): description.
                Returns:
                    type: description.

                Function:
                {code_snippet}
                """
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        result = response.json()
        docstring = result["response"].strip()
        docstring = docstring.replace("```python", "").replace("```", "").strip()
        return docstring

    def add_docstrings_to_file(self, file_path, previous_file_path=None):
        """
        Summary:
        Generates docstrings for functions in a Python file based on the changes between the current and previous versions of the file.

        Args:
            file_path (str): The path to the Python file.
            previous_file_path (str, optional): The path to the previous version of the file.

        Returns:
            None
        """
        print(f"📝 Running docstring generator on {file_path}")

        with open(file_path, "r") as file:
            current_source = file.read()

        if previous_file_path:
            with open(previous_file_path, "r") as prev_file:
                previous_source = prev_file.read()
        else:
            print("⚠️ No previous file provided. Generating docstrings for all methods.")
            previous_source = ""

        # Use get_changed_lines to find changes
        diff = difflib.unified_diff(
            previous_source.splitlines(keepends=True),
            current_source.splitlines(keepends=True),
            lineterm="",
        )
        changed_lines = set()
        for line in diff:
            if line.startswith("@@"):
                parts = line.split()
                current_lines = parts[2]
                start_line, _, length = current_lines[1:].partition(",")
                start_line = int(start_line)
                length = int(length) if length else 1
                changed_lines.update(range(start_line, start_line + length))

        tree = ast.parse(current_source)
        new_lines = current_source.splitlines(keepends=True)
        offset = 0

        for node in ast.walk(tree):
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and ast.get_docstring(node) is None
            ):
                if not node.body:
                    continue

                start_line = node.lineno
                if previous_file_path and start_line not in changed_lines:
                    continue  # Skip unchanged methods

                if not previous_file_path and start_line not in changed_lines:
                    continue  # Skip unchanged methods when no previous file is provided

                indent = " " * (node.col_offset + 4)

                # Extract only the function body
                function_body_lines = current_source.splitlines()[
                    node.lineno : node.end_lineno
                ]
                function_body = "\n".join(
                    line[len(indent) :] for line in function_body_lines[1:]
                )

                try:
                    print(f"🔍 Generating docstring for: {node.name}")
                    docstring = self.generate_docstring(function_body)

                    # Clean and prepare docstring lines
                    cleaned = docstring.strip().strip('"""').strip("'''").strip()
                    cleaned = cleaned.replace('"""', '\\"\\"\\"')
                    docstring_lines = [f'{indent}"""']
                    for line in cleaned.splitlines():
                        docstring_lines.append(f"{indent}{line}")
                    docstring_lines.append(f'{indent}"""')

                    # Insert docstring after function definition
                    def_line = node.lineno - 1
                    insert_at = def_line + 1 + offset
                    new_lines[insert_at:insert_at] = [
                        line + "\n" for line in docstring_lines
                    ]
                    offset += len(docstring_lines)
                except Exception as e:
                    print(f"❌ Failed for {node.name}: {e}")

        with open(file_path, "w") as file:
            file.writelines(new_lines)

        print(f"✅ Docstrings added in: {file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python doc_string.py <file.py> [<previous_file.py>]")
        sys.exit(1)

    file_path = sys.argv[1]
    previous_file = sys.argv[2] if len(sys.argv) > 2 else None
    ollama = OllamaAPI()
    ollama.add_docstrings_to_file(file_path, previous_file_path=previous_file)
