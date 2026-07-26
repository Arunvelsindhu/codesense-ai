import os
from collections import Counter

from app.ingestion.chunker import chunk_repo, get_language_from_file
from app.tools.static_analysis import run_ruff
from app.memory import session_store


def _language_breakdown(repo_path: str) -> dict:
    counts = Counter()
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in {"node_modules", "venv", ".git", "__pycache__", "dist", "build"}]
        for file in files:
            lang = get_language_from_file(os.path.join(root, file))
            if lang:
                counts[lang] += 1
    return dict(counts)


def _issue_severity_breakdown(repo_path: str) -> dict:
    """Buckets ruff issue codes by their prefix letter, which roughly maps
    to category (E/W = style, F = logic errors/pyflakes, I = imports, etc.)"""
    issues = run_ruff(repo_path)
    counts = Counter()
    for issue in issues:
        code = issue.get("code") or ""
        prefix = "".join(ch for ch in code if ch.isalpha()) or "other"
        counts[prefix] += 1
    return {"total_issues": len(issues), "by_category": dict(counts)}


def generate_eval_metrics(repo_name: str) -> dict:
    """
    Computes a snapshot of evaluation/metrics data for a repo: chunk and
    language coverage, static analysis issue counts, and how much the chat
    has been used for this repo (including how often it had to fall back
    to "not enough context", as a rough grounding-quality signal).
    """
    repo_path = os.path.join("cloned_repos", repo_name)

    metrics = {
        "repo_name": repo_name,
        "language_breakdown": {},
        "static_analysis": {"total_issues": 0, "by_category": {}},
        "chat": {"total_messages": 0, "user_questions": 0, "ungrounded_answers": 0},
    }

    if os.path.exists(repo_path):
        chunks = chunk_repo(repo_path)
        metrics["total_chunks"] = len(chunks)
        metrics["language_breakdown"] = _language_breakdown(repo_path)
        metrics["static_analysis"] = _issue_severity_breakdown(repo_path)

    history = session_store.get_history(repo_name)
    user_questions = [m for m in history if m["role"] == "user"]
    ungrounded = [
        m for m in history
        if m["role"] == "assistant" and "don't have enough context" in m["text"].lower()
    ]
    metrics["chat"] = {
        "total_messages": len(history),
        "user_questions": len(user_questions),
        "ungrounded_answers": len(ungrounded),
    }

    return metrics


def format_eval_metrics_markdown(metrics: dict) -> str:
    lang_lines = "\n".join(
        f"- **{lang}**: {count} file(s)" for lang, count in metrics.get("language_breakdown", {}).items()
    ) or "- No supported source files detected."

    sa = metrics.get("static_analysis", {})
    sa_lines = "\n".join(
        f"- **{category}**: {count} issue(s)" for category, count in sa.get("by_category", {}).items()
    ) or "- No static analysis issues found."

    chat = metrics.get("chat", {})
    grounding_rate = "n/a"
    if chat.get("user_questions"):
        answered = chat["user_questions"] - chat.get("ungrounded_answers", 0)
        grounding_rate = f"{round(100 * answered / chat['user_questions'])}%"

    return f"""## Evaluation & Metrics

**Chunks indexed:** {metrics.get('total_chunks', 'n/a')}

**Language breakdown:**
{lang_lines}

**Static analysis findings ({sa.get('total_issues', 0)} total):**
{sa_lines}

**Chat usage for this session:**
- Questions asked: {chat.get('user_questions', 0)}
- Answered with grounded context: {grounding_rate}
- Fell back to "not enough context": {chat.get('ungrounded_answers', 0)}
"""
