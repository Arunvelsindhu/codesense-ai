import chromadb
from app.core.config import settings

client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

def get_or_create_collection(repo_name: str):
    return client.get_or_create_collection(
        name=repo_name,
        metadata={"hnsw:space": "cosine"},
    )

def store_chunks(repo_name: str, embedded_chunks: list):
    collection = get_or_create_collection(repo_name)

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for i, chunk in enumerate(embedded_chunks):
        ids.append(f"{repo_name}_{i}")
        documents.append(chunk["code"])
        embeddings.append(chunk["embedding"])
        metadatas.append({
            "file": chunk["file"],
            "type": chunk["type"],
            "name": chunk["name"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
        })

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(ids)