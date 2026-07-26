# This logic is currently handled directly inside app/agents/orchestrator.py (architecture_node)
# Kept as a thin re-export for structural consistency with the planned architecture

from app.agents.doc_generator_agent import generate_readme

def run_architecture_analysis(repo_name: str, chunks: list) -> str:
    return generate_readme(repo_name, chunks)