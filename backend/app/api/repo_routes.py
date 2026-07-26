import json
import os
import subprocess

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.repo_schema import RepoRequest, RepoIngestRequest
from app.ingestion.chunker import chunk_repo
from app.ingestion.embedder import embed_chunks
from app.retrieval.vector_store import store_chunks
from app.tools.github_tool import clone_repository
from app.agents.orchestrator import run_full_analysis, run_full_analysis_stream
from app.memory import session_store

router = APIRouter()


@router.post("/repo/clone")
def clone_repo(request: RepoRequest):
    try:
        result = clone_repository(request.repo_url, github_token=request.github_token)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"Clone failed: {e.stderr}")

    session_store.remember_repo_url(result["repo_name"], request.repo_url)

    message = "Repo already cloned" if result["already_cloned"] else "Repo cloned successfully"
    return {"message": message, "path": result["path"], "repo_name": result["repo_name"]}


@router.post("/repo/ingest")
def ingest_repo(request: RepoIngestRequest):
    repo_path = os.path.join("cloned_repos", request.repo_name)

    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Repo not found. Clone it first.")

    chunks = chunk_repo(repo_path)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunkable code found in repo.")

    embedded_chunks = embed_chunks(chunks)
    stored_count = store_chunks(request.repo_name, embedded_chunks)
    session_store.mark_repo_ingested(request.repo_name)

    return {
        "message": "Repo ingested successfully",
        "total_chunks_found": len(chunks),
        "chunks_embedded_and_stored": stored_count,
    }


@router.post("/repo/analyze")
def analyze_repo(request: RepoIngestRequest):
    repo_path = os.path.join("cloned_repos", request.repo_name)
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Repo not found. Clone it first.")

    result = run_full_analysis(request.repo_name)
    session_store.save_analysis(request.repo_name, session_store.get_repo_url(request.repo_name), result)
    return result


@router.get("/repo/analyze/stream")
def analyze_repo_stream(repo_name: str):
    """
    Server-Sent Events version of /repo/analyze. Streams a progress event
    as each pipeline stage (ingest -> embed -> architecture -> code_analysis)
    completes, then a final "complete" event with the full result.
    """
    repo_path = os.path.join("cloned_repos", repo_name)
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Repo not found. Clone it first.")

    def event_stream():
        for event in run_full_analysis_stream(repo_name):
            if event["event"] == "complete":
                session_store.save_analysis(repo_name, session_store.get_repo_url(repo_name), event["result"])
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/repo/list")
def list_repos():
    """Repo history: every repo that has been fully analyzed, most recent first."""
    return {"repos": session_store.list_analyzed_repos()}


@router.get("/repo/{repo_name}")
def get_repo(repo_name: str):
    """Fetch a previously analyzed repo's cached results without re-running analysis."""
    result = session_store.get_analysis(repo_name)
    if not result:
        raise HTTPException(status_code=404, detail="No cached analysis for this repo. Analyze it first.")
    return result
