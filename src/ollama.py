import ollama

SYSTEM_PROMPT = "You are a code review assistant. Identify any issues or improvements in the code diff. Reply concisely with actionable suggestions."

def get_review_from_ollama(file_path, code_diff):
    print(f"[INFO] Sending diff for {file_path} to Ollama (model: codellama)...")
    prompt = f"Filename: {file_path}\n\nCode diff:\n{code_diff}"
    response = ollama.chat(
        model='codellama',
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )
    print("[INFO] Ollama response received.")
    return response['message']['content']