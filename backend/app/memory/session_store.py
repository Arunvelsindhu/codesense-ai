# Session/history store, backed by SQLite so it survives a server restart
# or a page refresh (see app/core/db.py). Public functions here are kept
# stable so the rest of the app doesn't need to care about storage details.

from app.core import db

db.init_db()

# Repos ingested during this process (fast in-memory check, avoids a
# round trip for something we already know for the current run).
_ingested_repos = set()

# repo_name -> original clone URL, set at clone time so analysis records
# can store the real URL instead of just the repo name.
_repo_urls = {}


def remember_repo_url(repo_name: str, repo_url: str):
    _repo_urls[repo_name] = repo_url


def get_repo_url(repo_name: str) -> str:
    return _repo_urls.get(repo_name, repo_name)


def mark_repo_ingested(repo_name: str):
    _ingested_repos.add(repo_name)


def is_repo_ingested(repo_name: str) -> bool:
    if repo_name in _ingested_repos:
        return True
    return db.get_repo_analysis(repo_name) is not None


def add_message(repo_name: str, role: str, text: str):
    db.add_chat_message(repo_name, role, text)


def get_history(repo_name: str) -> list:
    return [{"role": m["role"], "text": m["text"]} for m in db.get_chat_history(repo_name)]


def save_analysis(repo_name: str, repo_url: str, result: dict):
    mark_repo_ingested(repo_name)
    db.upsert_repo_analysis(repo_name, repo_url, result)


def get_analysis(repo_name: str) -> dict | None:
    return db.get_repo_analysis(repo_name)


def list_analyzed_repos() -> list:
    return db.list_repos()


def delete_analysis(repo_name: str):
    _ingested_repos.discard(repo_name)
    db.delete_repo(repo_name)
