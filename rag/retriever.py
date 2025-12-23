import os
import pickle
import faiss
import numpy as np
from ingestion.embeddings import embed

VECTOR_BASE = "vector_store"


def retrieve(question: str, k_per_book: int = 3):
    """
    Balanced per-book retrieval:
    - Search each book independently
    - Take top-k from each book
    - Prevent early-book dominance
    """
    q_vec = embed([question])[0]
    all_chunks = []

    for book_dir in os.listdir(VECTOR_BASE):
        book_path = os.path.join(VECTOR_BASE, book_dir)

        index_path = os.path.join(book_path, "index.faiss")
        meta_path = os.path.join(book_path, "meta.pkl")

        if not os.path.exists(index_path):
            continue

        index = faiss.read_index(index_path)

        with open(meta_path, "rb") as f:
            metadata = pickle.load(f)

        _, ids = index.search(np.array([q_vec]), k_per_book)

        for idx in ids[0]:
            if idx < len(metadata):
                all_chunks.append(metadata[idx])

    return all_chunks


def filter_chunks(question: str, chunks: list):
    """
    Light lexical relevance filter to remove noisy early-book chunks
    while keeping a safe fallback.
    """
    q = question.lower()

    KEYWORDS = [
        "horcrux",
        "soul",
        "slughorn",
        "voldemort",
        "deathly",
        "hallow",
        "elder wand",
        "resurrection stone",
        "invisibility cloak",
    ]

    filtered = []
    for c in chunks:
        text = c.get("text", "").lower()
        if any(k in text for k in KEYWORDS if k in q):
            filtered.append(c)

    # Fallback: if filtering removes everything, return original chunks
    return filtered if filtered else chunks