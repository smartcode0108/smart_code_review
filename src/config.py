REVIEW_CONFIG = {
    "emojis": {
        "type-safety": "🔒",
        "architecture": "🏗️",
        "readability": "📖",
        "security": "🛡️",
        "performance": "⚡",
        "suggestion": "💡",
        "good-practice": "✨",
        "blocking": "🚫",
        "ai-suggestion": "🤖",
        "ai-issue": "⚠️",
        "ai-praise": "👏",
    },
    "concurrencyLimit": 3,
    "supportedExtensions": r".(js|jsx|ts|tsx|py|go|java|rb|php|cs)$",
    "maxFileSize": 500000,  # 500KB
    "reviewPrompt": """You are an expert code reviewer. Review the code from file `{filename}`.
Only provide feedback for the following lines: {changed_lines}.
Each line starts with its line number and a [CHANGED] tag if modified.

Focus on:
- Type safety
- Design patterns
- Readability and maintainability
- Security issues (use the exact line of risk)
- Performance

Return JSON output like this:
[
  {{
    "line": (line_number_as_int),
    "type": (type_as_string): one of ["security", "perfomance", "design", "readability", "bug", "suggestion"],
    "severity": (severity_as_string): "low", "medium", or "high",
    "message": "<specific_issue_and_recommendation>"
  }}
]

Code:
{content}
"""
}