import json
from pathlib import Path

import faiss
import numpy as np
import ollama


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

RAG_DIR = Path(__file__).resolve().parent

INDEX_PATH = RAG_DIR / "index" / "banking.faiss"
METADATA_PATH = RAG_DIR / "index" / "metadata.json"


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_TOP_K = 5
MAX_TOP_K = 20


# ---------------------------------------------------------
# Load FAISS index + metadata
# ---------------------------------------------------------

def load_index():
    """
    Load the FAISS vector index and corresponding metadata.
    """

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_PATH}"
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_PATH}"
        )

    index = faiss.read_index(str(INDEX_PATH))

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    if index.ntotal != len(metadata):
        raise ValueError(
            "FAISS index and metadata are inconsistent: "
            f"{index.ntotal} vectors vs "
            f"{len(metadata)} metadata records"
        )

    return index, metadata


# ---------------------------------------------------------
# Query embedding
# ---------------------------------------------------------

def embed_query(query: str) -> np.ndarray:
    """
    Convert a natural-language query into an embedding.
    """

    if not isinstance(query, str):
        raise TypeError("Query must be a string.")

    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=query
    )

    vector = np.asarray(
        response["embeddings"][0],
        dtype="float32"
    ).reshape(1, -1)

    # Normalize exactly as done during index construction.
    faiss.normalize_L2(vector)

    return vector


# ---------------------------------------------------------
# Public RAG API
# ---------------------------------------------------------

def search_knowledge(
    query: str,
    top_k: int = DEFAULT_TOP_K
) -> dict:
    """
    Search the controlled banking knowledge base.

    Parameters
    ----------
    query : str
        Natural-language banking question.

    top_k : int
        Number of relevant knowledge chunks to retrieve.

    Returns
    -------
    dict
        Contract-compatible RAG response:

        {
            "success": True,
            "query": "...",
            "results": [
                {
                    "content": "...",
                    "source": "...",
                    "score": 0.87
                }
            ]
        }
    """

    # -----------------------------
    # Validate input
    # -----------------------------

    if not isinstance(query, str):
        return {
            "success": False,
            "query": query,
            "results": [],
            "error": "Query must be a string."
        }

    query = query.strip()

    if not query:
        return {
            "success": False,
            "query": query,
            "results": [],
            "error": "Query cannot be empty."
        }

    if not isinstance(top_k, int):
        return {
            "success": False,
            "query": query,
            "results": [],
            "error": "top_k must be an integer."
        }

    if top_k < 1:
        return {
            "success": False,
            "query": query,
            "results": [],
            "error": "top_k must be at least 1."
        }

    top_k = min(top_k, MAX_TOP_K)

    # -----------------------------
    # Load index
    # -----------------------------

    try:
        index, metadata = load_index()

    except Exception as error:
        return {
            "success": False,
            "query": query,
            "results": [],
            "error": str(error)
        }

    if index.ntotal == 0:
        return {
            "success": False,
            "query": query,
            "results": [],
            "error": "Knowledge base is empty."
        }

    # -----------------------------
    # Create query embedding
    # -----------------------------

    try:
        query_vector = embed_query(query)

    except Exception as error:
        return {
            "success": False,
            "query": query,
            "results": [],
            "error": f"Embedding generation failed: {error}"
        }

    # -----------------------------
    # FAISS similarity search
    # -----------------------------

    number_of_results = min(
        top_k,
        index.ntotal
    )

    scores, indices = index.search(
        query_vector,
        number_of_results
    )

    # -----------------------------
    # Format results
    # -----------------------------

    results = []

    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id < 0:
            continue

        metadata_item = metadata[index_id]

        # Our current metadata stores the actual
        # knowledge text under "text".
        content = metadata_item.get(
            "text",
            metadata_item.get("content", "")
        )

        source = metadata_item.get(
            "source",
            "unknown"
        )

        results.append(
            {
                "content": content,
                "source": source,
                "score": float(score)
            }
        )

    return {
        "success": True,
        "query": query,
        "results": results
    }


# ---------------------------------------------------------
# Manual test
# ---------------------------------------------------------

if __name__ == "__main__":

    query = "What is the interest rate for a personal loan?"

    response = search_knowledge(
        query,
        top_k=3
    )

    print("=" * 70)
    print("RAG SEARCH TEST")
    print("=" * 70)

    print("\nQuery:")
    print(response["query"])

    print("\nSuccess:")
    print(response["success"])

    print("\nResults:")

    for rank, result in enumerate(
        response["results"],
        start=1
    ):

        print("\n" + "-" * 70)

        print(f"Rank: {rank}")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {result['source']}")

        print("\nContent:")
        print(result["content"][:500])

    print("\n" + "=" * 70)