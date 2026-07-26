# This logic is currently handled directly inside app/tools/github_tool.py
# Kept as a thin re-export for structural consistency with the planned architecture

from app.tools.github_tool import clone_repository

def load_repo(repo_url: str) -> dict:
    return clone_repository(repo_url)