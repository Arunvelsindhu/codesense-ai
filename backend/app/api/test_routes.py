from fastapi import APIRouter, HTTPException
import os

from app.models.repo_schema import RepoIngestRequest
from app.ingestion.chunker import chunk_repo
from app.agents.test_writer_agent import generate_unit_test

router = APIRouter()


@router.post("/tests/generate")
def get_unit_test(request: RepoIngestRequest, function_name: str):
    repo_path = os.path.join("cloned_repos", request.repo_name)
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Repo not found. Clone it first.")

    chunks = chunk_repo(repo_path)
    clean_name = function_name.strip()
    match = next((c for c in chunks if clean_name.lower() in c["name"].lower()), None)

    if not match:
        raise HTTPException(status_code=404, detail=f"Function/class '{clean_name}' not found.")

    test_code = generate_unit_test(match)
    return {"name": match["name"], "unit_test": test_code}