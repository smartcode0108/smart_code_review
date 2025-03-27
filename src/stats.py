class ReviewStats:
    def __init__(self):
        self.stats = {
            "typeSafetyIssues": 0,
            "architectureIssues": 0,
            "readabilityIssues": 0,
            "securityIssues": 0,
            "performanceIssues": 0,
            "suggestions": 0,
            "goodPatterns": 0,
            "blockingIssues": 0,
            "aiSuggestions": 0,
            "aiIssues": 0,
            "aiPraises": 0,
        }
        self.issues_by_type = {}
        self.high_severity_issues = []

    def update_stats(self, issue_type, severity, message, file, line):
        # Update count based on type
        if issue_type == "type-safety":
            self.stats["typeSafetyIssues"] += 1
        elif issue_type == "architecture":
            self.stats["architectureIssues"] += 1
        elif issue_type == "readability":
            self.stats["readabilityIssues"] += 1
        elif issue_type == "security":
            self.stats["securityIssues"] += 1
        elif issue_type == "performance":
            self.stats["performanceIssues"] += 1
        elif issue_type == "suggestion":
            self.stats["suggestions"] += 1
        elif issue_type == "good-practice":
            self.stats["goodPatterns"] += 1

        # Track high severity issues
        if severity == "high":
            self.high_severity_issues.append({
                "type": issue_type,
                "message": message,
                "file": file,
                "line": line,
            })

        # Group issues by type
        if issue_type not in self.issues_by_type:
            self.issues_by_type[issue_type] = []
        self.issues_by_type[issue_type].append({
            "severity": severity,
            "message": message,
            "file": file,
            "line": line,
        })

    def generate_summary(self):
        total_issues = sum(self.stats.values())

        summary = "## 🔍 Code Review Summary\n\n"

        # Overall statistics
        summary += "### 📊 Overall Statistics\n"
        summary += f"- Total issues found: {total_issues}\n"
        summary += f"- High severity issues: {len(self.high_severity_issues)}\n"
        summary += f"- Type safety issues: {self.stats['typeSafetyIssues']}\n"
        summary += f"- Architecture issues: {self.stats['architectureIssues']}\n"
        summary += f"- Security concerns: {self.stats['securityIssues']}\n"
        summary += f"- Performance issues: {self.stats['performanceIssues']}\n"
        summary += f"- Readability improvements: {self.stats['readabilityIssues']}\n"
        summary += f"- Suggestions: {self.stats['suggestions']}\n"
        summary += f"- Good patterns identified: {self.stats['goodPatterns']}\n\n"

        # High severity issues section
        if self.high_severity_issues:
            summary += "### ❗ High Priority Issues\n"
            for issue in self.high_severity_issues:
                summary += f"- {issue['type'].upper()}: {issue['message']} ({issue['file']}:{issue['line']})\n"
            summary += "\n"

        # Detailed breakdown by type
        summary += "### 📝 Detailed Breakdown\n"
        for issue_type, issues in self.issues_by_type.items():
            if issues:
                summary += f"\n#### {issue_type.upper()}\n"
                grouped_by_severity = {}
                for issue in issues:
                    grouped_by_severity.setdefault(issue["severity"], []).append(issue)

                for severity in ["high", "medium", "low"]:
                    if severity in grouped_by_severity:
                        summary += f"\n**{severity.upper()}**:\n"
                        for issue in grouped_by_severity[severity]:
                            summary += f"- {issue['message']} ({issue['file']}:{issue['line']})\n"

        return summary