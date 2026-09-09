from rag.loader import load_knowledge_base


def create_chunks(documents):
    """
    Convert loaded knowledge documents into
    smaller retrieval-friendly chunks.

    Each chunk keeps the original metadata.
    """

    chunks = []

    for doc in documents:
        text = doc["text"]

        # For our current structured banking records,
        # each record is already small enough to remain
        # as one semantic chunk.
        chunk = {
            "chunk_id": f"{doc['source']}::{doc['record_id']}",
            "text": text,
            "source": doc["source"],
            "category": doc["category"],
            "subcategory": doc["subcategory"],
            "record_id": doc["record_id"],
        }

        chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    documents = load_knowledge_base()
    chunks = create_chunks(documents)

    print("CHUNKING: PASS")
    print("Documents:", len(documents))
    print("Chunks:", len(chunks))

    print("\n--- Sample Chunk ---")
    print("Chunk ID:", chunks[0]["chunk_id"])
    print("Source:", chunks[0]["source"])
    print("Category:", chunks[0]["category"])
    print("Text:")
    print(chunks[0]["text"])