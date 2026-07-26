import subprocess
import json

def run_static_analysis(repo_path: str) -> list:
    """
    Runs ruff on the repo and returns a list of issues found.
    """
    try:
        result = subprocess.run(
            ["ruff", "check", repo_path, "--output-format=json"],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            issues = json.loads(result.stdout)
            return [
                {
                    "file": issue.get("filename"),
                    "line": issue.get("location", {}).get("row"),
                    "message": issue.get("message"),
                    "code": issue.get("code"),
                }
                for issue in issues
            ]
        return []
    except Exception as e:
        return [{"error": str(e)}]


def summarize_issues_with_llm(issues: list) -> str:
    from app.core.llm import get_llm_response

    if not issues:
        return "No static analysis issues found."

    issues_text = "\n".join(
        f"- {i.get('file')}:{i.get('line')} [{i.get('code')}] {i.get('message')}"
        for i in issues[:30]
    )

    prompt = f"""You are a senior code reviewer. Below is a list of static analysis issues found by a linter.
Summarize the most important ones a developer should fix first, and explain why, in plain language.

ISSUES:
{issues_text}

SUMMARY:"""

    return get_llm_response(prompt)