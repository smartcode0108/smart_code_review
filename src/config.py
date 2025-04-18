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
    "line": 42,
    "type": "security",
    "severity": "high",
    "message": "<specific_issue_and_recommendation>"
  }}
]

Code:
{content}
"""
}