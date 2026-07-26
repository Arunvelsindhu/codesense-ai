from app.retrieval.vector_store import get_or_create_collection
from app.core.llm import get_embedding

# Cosine distance from Chroma ranges 0 (identical) to 2 (opposite).
# Anything above this is treated as "not actually relevant" to the question,
# so the chunk is dropped before it ever reaches the LLM as context.
MAX_RELEVANT_DISTANCE = 0.75


def retrieve_relevant_chunks(repo_name: str, query: str, top_k: int = 5):
    """
    Retrieves the top_k most similar chunks to `query`, then filters out
    anything that isn't actually close enough to be considered relevant.
    This is the grounding check: if nothing passes the threshold, the
    caller gets an empty list back instead of weakly-related code that
    would otherwise get fed to the LLM as if it were solid context.
    """
    collection = get_or_create_collection(repo_name)

    if collection.count() == 0:
        return []

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    chunks = []
    for code, metadata, distance in zip(documents, metadatas, distances):
        if distance > MAX_RELEVANT_DISTANCE:
            continue
        chunks.append({
            "code": code,
            "metadata": metadata,
            "distance": distance,
            "relevance": round(max(0.0, 1 - distance / 2), 4),
        })

    return chunks
