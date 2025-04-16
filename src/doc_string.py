import ast
import os
import sys
import requests


class OllamaAPI:
    def __init__(self, model="codellama"):
        self.base_url = "http://127.0.0.1:11434"
        self.model = model

    def generate_docstring(self, function_code):
        prompt = f"Generate a concise, clear Python docstring for the following function:\n\n{function_code}\n\n\"\"\""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            result = response.json()
            docstring = result.get("response", "").strip()
            return docstring.replace('"""', '').strip()
        except Exception as e:
            print(f"⚠️ Error generating docstring: {e}")
            return "TODO: Add docstring"

    def add_docstrings_to_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        with open(file_path, "r") as f:
            code = f.read()

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            print(f"Failed to parse {file_path}: {e}")
            return

        lines = code.splitlines()
        insertions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                func_start = node.lineno - 1
                func_code = "\n".join(lines[func_start : func_start + 10])
                print(f"Generating docstring for: {node.name} in {file_path}")
                docstring = self.generate_docstring(func_code)
                insertions.append((func_start + 1, f'    """{docstring}"""'))

        for lineno, doc in reversed(insertions):
            lines.insert(lineno, doc)

        with open(file_path, "w") as f:
            f.write("\n".join(lines))
        print(f"✅ Docstrings added in: {file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_docstrings.py <file.py>")
        sys.exit(1)

    file_path = sys.argv[1]
    ollama = OllamaAPI()
    ollama.add_docstrings_to_file(file_path)
