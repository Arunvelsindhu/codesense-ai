# This logic is currently handled directly inside app/agents/orchestrator.py (ingestion_node)
# Kept as a thin re-export for structural consistency with the planned architecture

from app.ingestion.chunker import chunk_repo

def run_ingestion(repo_path: str) -> list:
    return chunk_repo(repo_path)