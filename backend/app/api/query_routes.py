from fastapi import APIRouter, HTTPException

from app.models.query_schema import QueryRequest
from app.models.response_schema import QueryResponse
from app.retrieval.retriever import retrieve_relevant_chunks
from app.retrieval.vector_store import get_or_create_collection
from app.core.llm import get_llm_response
from app.memory.session_store import add_message

router = APIRouter()

NO_CONTEXT_ANSWER = (
    "I don't have enough context to answer that. Nothing in this repository's "
    "indexed code looked closely related to your question — try rephrasing it, "
    "or ask about something more specific to the codebase."
)


@router.post("/query", response_model=QueryResponse)
def query_repo(request: QueryRequest):
    collection = get_or_create_collection(request.repo_name)
    if collection.count() == 0:
        raise HTTPException(
            status_code=404,
            detail="No relevant code found. Did you ingest this repo?",
        )

    add_message(request.repo_name, "user", request.question)

    relevant_chunks = retrieve_relevant_chunks(request.repo_name, request.question)

    if not relevant_chunks:
        add_message(request.repo_name, "assistant", NO_CONTEXT_ANSWER)
        return QueryResponse(answer=NO_CONTEXT_ANSWER, sources=[])

    context = "\n\n---\n\n".join(
        f"File: {c['metadata']['file']} ({c['metadata']['name']})\n{c['code']}"
        for c in relevant_chunks
    )

    prompt = f"""You are a helpful AI software engineer assistant.
Answer the user's question about this codebase using ONLY the context below.
The context has already been filtered for relevance, but it may still be incomplete.
If the context genuinely does not contain enough information to answer the question,
reply with exactly: "I don't have enough context to answer that." Do not guess or
invent details that aren't supported by the context.

CONTEXT:
{context}

QUESTION: {request.question}

ANSWER:"""

    answer = get_llm_response(prompt)

    sources = [c["metadata"] for c in relevant_chunks]

    add_message(request.repo_name, "assistant", answer)

    return QueryResponse(answer=answer, sources=sources)
