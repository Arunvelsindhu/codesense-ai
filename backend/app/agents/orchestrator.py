from typing import TypedDict, List, Optional, Iterator
from langgraph.graph import StateGraph, END

from app.ingestion.chunker import chunk_repo
from app.ingestion.embedder import embed_chunks
from app.retrieval.vector_store import store_chunks
from app.agents.doc_generator_agent import generate_readme
from app.agents.code_analysis_agent import run_static_analysis, summarize_issues_with_llm
import os


class RepoAnalysisState(TypedDict):
    repo_name: str
    repo_path: str
    chunks: List[dict]
    embedded_count: int
    readme: Optional[str]
    issues_summary: Optional[str]


# Human-readable labels shown to the frontend while each node is running,
# keyed by the node name that just *finished* streaming in.
NODE_LABELS = {
    "ingest": "Scanning repository and chunking code...",
    "embed": "Generating embeddings and indexing chunks...",
    "architecture": "Writing architecture overview...",
    "code_analysis": "Running static analysis...",
}


def ingestion_node(state: RepoAnalysisState) -> RepoAnalysisState:
    chunks = chunk_repo(state["repo_path"])
    state["chunks"] = chunks
    return state


def embedding_node(state: RepoAnalysisState) -> RepoAnalysisState:
    embedded_chunks = embed_chunks(state["chunks"])
    count = store_chunks(state["repo_name"], embedded_chunks)
    state["embedded_count"] = count
    return state


def architecture_node(state: RepoAnalysisState) -> RepoAnalysisState:
    readme = generate_readme(state["repo_name"], state["chunks"])
    state["readme"] = readme
    return state


def code_analysis_node(state: RepoAnalysisState) -> RepoAnalysisState:
    issues = run_static_analysis(state["repo_path"])
    summary = summarize_issues_with_llm(issues)
    state["issues_summary"] = summary
    return state


def build_graph():
    graph = StateGraph(RepoAnalysisState)

    graph.add_node("ingest", ingestion_node)
    graph.add_node("embed", embedding_node)
    graph.add_node("architecture", architecture_node)
    graph.add_node("code_analysis", code_analysis_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "embed")
    graph.add_edge("embed", "architecture")
    graph.add_edge("architecture", "code_analysis")
    graph.add_edge("code_analysis", END)

    return graph.compile()


def _initial_state(repo_name: str) -> RepoAnalysisState:
    repo_path = os.path.join("cloned_repos", repo_name)
    return {
        "repo_name": repo_name,
        "repo_path": repo_path,
        "chunks": [],
        "embedded_count": 0,
        "readme": None,
        "issues_summary": None,
    }


def _format_result(final_state: RepoAnalysisState) -> dict:
    return {
        "repo_name": final_state["repo_name"],
        "total_chunks": len(final_state["chunks"]),
        "chunks_embedded": final_state["embedded_count"],
        "readme": final_state["readme"],
        "code_issues_summary": final_state["issues_summary"],
    }


def run_full_analysis(repo_name: str) -> dict:
    """Blocking version: runs the whole pipeline and returns the final result."""
    graph = build_graph()
    final_state = graph.invoke(_initial_state(repo_name))
    return _format_result(final_state)


def run_full_analysis_stream(repo_name: str) -> Iterator[dict]:
    """
    Streaming version: yields a progress event as each LangGraph node
    completes, then a final "complete" event with the full result.
    Each node function returns the *entire* state object (not a partial
    delta), so the value from the latest step is always the full
    accumulated state - no manual merging needed.
    """
    graph = build_graph()
    final_state = None

    for update in graph.stream(_initial_state(repo_name), stream_mode="updates"):
        node_name = next(iter(update))
        node_state = update[node_name]
        final_state = node_state

        yield {
            "event": "progress",
            "node": node_name,
            "message": NODE_LABELS.get(node_name, f"Running {node_name}..."),
        }

    if final_state is None:
        yield {"event": "error", "message": "Analysis pipeline produced no output."}
        return

    yield {
        "event": "complete",
        "result": _format_result(final_state),
    }
