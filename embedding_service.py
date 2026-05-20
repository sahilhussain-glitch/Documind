"""FAISS vector index management for document embeddings."""
import os
import json
import numpy as np
from typing import List, Tuple

import faiss
from openai import OpenAI

from backend.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

# In-memory store: maps (doc_id, chunk_index) → chunk_text
_chunk_store: dict[str, dict[int, str]] = {}   # doc_id → {chunk_idx: text}

# Global FAISS index
_index: faiss.IndexFlatL2 | None = None
_index_meta: list[dict] = []          # [{"doc_id": ..., "chunk_index": ...}, ...]
_EMBED_DIM = 1536                     # text-embedding-3-small dimension


def _get_index() -> faiss.IndexFlatL2:
    global _index
    if _index is None:
        _index = faiss.IndexFlatL2(_EMBED_DIM)
    return _index


def _embed_texts(texts: List[str]) -> np.ndarray:
    """Call OpenAI Embeddings API and return numpy array."""
    response = client.embeddings.create(
        model=settings.embed_model,
        input=texts,
    )
    vectors = [item.embedding for item in response.data]
    return np.array(vectors, dtype=np.float32)


def index_document(doc_id: str, chunks: List[str]) -> None:
    """Embed all chunks and add them to the FAISS index."""
    idx = _get_index()

    # Store chunks in memory
    _chunk_store[doc_id] = {i: chunk for i, chunk in enumerate(chunks)}

    # Embed in batches of 100
    batch_size = 100
    for batch_start in range(0, len(chunks), batch_size):
        batch = chunks[batch_start: batch_start + batch_size]
        vectors = _embed_texts(batch)
        idx.add(vectors)

        for i, _ in enumerate(batch):
            _index_meta.append({
                "doc_id": doc_id,
                "chunk_index": batch_start + i,
            })


def search(query: str, top_k: int = 5, doc_ids: List[str] | None = None) -> List[dict]:
    """
    Semantic search over the index.
    Returns list of {doc_id, chunk_index, text, score}.
    """
    idx = _get_index()
    if idx.ntotal == 0:
        return []

    q_vec = _embed_texts([query])
    distances, indices = idx.search(q_vec, min(top_k * 3, idx.ntotal))

    results = []
    for dist, i in zip(distances[0], indices[0]):
        if i == -1:
            continue
        meta = _index_meta[i]
        if doc_ids and meta["doc_id"] not in doc_ids:
            continue
        text = _chunk_store.get(meta["doc_id"], {}).get(meta["chunk_index"], "")
        results.append({
            "doc_id": meta["doc_id"],
            "chunk_index": meta["chunk_index"],
            "text": text,
            "score": float(dist),
        })
        if len(results) >= top_k:
            break

    return results


def remove_document(doc_id: str) -> None:
    """Remove a document's chunks from the store (FAISS doesn't support deletion natively)."""
    _chunk_store.pop(doc_id, None)
    # Mark index entries as removed; full rebuild needed for production
    for meta in _index_meta:
        if meta["doc_id"] == doc_id:
            meta["doc_id"] = "__deleted__"
