import json
from pathlib import Path

import faiss
import numpy as np
import ollama

from rag.loader import load_knowledge_base
from rag.chunker import create_chunks


INDEX_DIR = Path(__file__).resolve().parent / "index"
INDEX_DIR.mkdir(exist_ok=True)

INDEX_PATH = INDEX_DIR / "banking.faiss"
METADATA_PATH = INDEX_DIR / "metadata.json"

EMBEDDING_MODEL = "nomic-embed-text"


def create_embeddings(chunks):
    """Generate embeddings for every RAG chunk."""

    embeddings = []

    for i, chunk in enumerate(chunks, start=1):
        print(f"Embedding {i}/{len(chunks)}...")

        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=chunk["text"]
        )

        embeddings.append(response["embeddings"][0])

    return np.array(embeddings, dtype="float32")


def build_index():
    print("Loading knowledge base...")

    documents = load_knowledge_base()
    chunks = create_chunks(documents)

    print(f"Documents loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")

    print("\nGenerating embeddings...")

    embeddings = create_embeddings(chunks)

    dimension = embeddings.shape[1]

    print(f"\nEmbedding dimension: {dimension}")

    # Cosine similarity through normalized inner product
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    with open(METADATA_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=2, ensure_ascii=False)

    print("\nFAISS INDEX: PASS")
    print("Vectors:", index.ntotal)
    print("Dimension:", dimension)
    print("Index:", INDEX_PATH)
    print("Metadata:", METADATA_PATH)


if __name__ == "__main__":
    build_index()