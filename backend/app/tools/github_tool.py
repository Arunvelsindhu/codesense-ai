import subprocess
import os
from urllib.parse import urlparse, urlunparse

from app.core.config import settings


def _authenticated_url(repo_url: str, token: str) -> str:
    """Injects a token into an https:// GitHub URL for authenticated cloning."""
    parsed = urlparse(repo_url)
    netloc = f"{token}@{parsed.netloc}"
    return urlunparse(parsed._replace(netloc=netloc))


def _scrub_token(text: str, token: str) -> str:
    if not text or not token:
        return text
    return text.replace(token, "***")


def clone_repository(repo_url: str, destination_folder: str = "cloned_repos", github_token: str = None) -> dict:
    """
    Clones a GitHub repo into destination_folder. Returns repo_name and path.
    If github_token is provided (or falls back to a server-configured one),
    it's used to authenticate the clone for private repos, and is scrubbed
    from any error messages before they're raised.
    """
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_path = os.path.join(destination_folder, repo_name)

    if os.path.exists(clone_path):
        return {"repo_name": repo_name, "path": clone_path, "already_cloned": True}

    os.makedirs(destination_folder, exist_ok=True)

    token = github_token or settings.github_token
    clone_url = repo_url
    if token and repo_url.startswith("https://"):
        clone_url = _authenticated_url(repo_url, token)

    try:
        subprocess.run(
            ["git", "clone", clone_url, clone_path],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        stderr = _scrub_token(e.stderr, token) if token else e.stderr
        raise subprocess.CalledProcessError(e.returncode, "git clone", output=e.output, stderr=stderr)

    return {"repo_name": repo_name, "path": clone_path, "already_cloned": False}
