import time
from app.core.llm import get_embedding


def embed_chunks(chunks: list) -> list:
    """
    Generate embeddings for each chunk.
    Skip only invalid chunks and print detailed errors.
    """

    embedded_chunks = []

    print("=" * 60)
    print(f"Total chunks received: {len(chunks)}")
    print("=" * 60)

    for i, chunk in enumerate(chunks):

        try:
            code = chunk.get("code", "").strip()

            if not code:
                print(f"[{i}] Empty chunk skipped.")
                continue

            embedding = get_embedding(code)

            if embedding is None:
                print(f"[{i}] Embedding returned None.")
                continue

            if not isinstance(embedding, list):
                print(f"[{i}] Invalid embedding type: {type(embedding)}")
                continue

            if len(embedding) == 0:
                print(f"[{i}] Empty embedding returned.")
                continue

            chunk["embedding"] = embedding
            embedded_chunks.append(chunk)

            print(f"[{i}] ✓ Embedded successfully")

            time.sleep(1)

        except Exception as e:
            print(f"[{i}] Embedding failed")
            print(e)

    print("=" * 60)
    print(f"Successfully embedded: {len(embedded_chunks)}")
    print("=" * 60)

    return embedded_chunks