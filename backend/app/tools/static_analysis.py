import subprocess
import json

def run_ruff(repo_path: str) -> list:
    """
    Runs ruff static analysis on a repo and returns a list of issues.
    """
    try:
        result = subprocess.run(
            ["ruff", "check", repo_path, "--output-format=json"],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        return [{"error": str(e)}]