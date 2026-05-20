"""Core RAG pipeline: retrieve → augment → generate."""
import json
from typing import List

from backend.services import embedding_service, llm_service
from backend.services.document_service import get_document_meta
from backend.models import QueryResponse, Source, SummarizeResponse, ExtractResponse, ClassifyResponse
from backend.config import get_settings

settings = get_settings()

# ── Prompt Templates ────────────────────────────────────────────────────────

QA_SYSTEM = """You are DocuMind, a precise document intelligence assistant.
Answer the user's question using ONLY the provided document excerpts.
If the answer is not in the excerpts, say "I could not find this in the provided documents."
Always cite which document/excerpt your answer comes from."""

SUMMARIZE_SYSTEM = """You are a professional document summarizer.
Produce a {style} summary of the provided document text.
- concise: 3-5 sentences capturing the core message
- detailed: structured paragraphs covering all major points
- bullets: 5-10 bullet points of key takeaways"""

EXTRACT_SYSTEM = """You are a precise data extraction engine.
Extract the requested fields from the document text.
Respond ONLY with a valid JSON object. Keys are the field names provided.
If a field is not found, set its value to null.
Do not include any explanation outside the JSON."""

CLASSIFY_SYSTEM = """You are a document classification expert.
Classify the document into exactly one of the provided categories.
Respond ONLY with a valid JSON object with keys:
  category (string), confidence (high|medium|low), reasoning (1 sentence)."""


# ── RAG Q&A ─────────────────────────────────────────────────────────────────

def answer_question(question: str, doc_ids: List[str] | None, top_k: int) -> QueryResponse:
    chunks = embedding_service.search(question, top_k=top_k, doc_ids=doc_ids)

    context_parts = []
    sources = []
    for chunk in chunks:
        meta = get_document_meta(chunk["doc_id"])
        filename = meta.filename if meta else chunk["doc_id"]
        context_parts.append(
            f"[Document: {filename}, Chunk #{chunk['chunk_index']}]\n{chunk['text']}"
        )
        sources.append(Source(
            doc_id=chunk["doc_id"],
            filename=filename,
            chunk_index=chunk["chunk_index"],
            excerpt=chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
        ))

    context = "\n\n---\n\n".join(context_parts) if context_parts else "No document context available."

    messages = [
        {"role": "system", "content": QA_SYSTEM},
        {"role": "user", "content": f"Document excerpts:\n{context}\n\nQuestion: {question}"},
    ]
    answer = llm_service.chat(messages)

    return QueryResponse(answer=answer, sources=sources, model_used=llm_service.model_name())


# ── Summarization ────────────────────────────────────────────────────────────

def summarize_document(doc_id: str, style: str) -> SummarizeResponse:
    # Retrieve broad chunks of this document
    chunks = embedding_service.search("summary overview main points", top_k=10, doc_ids=[doc_id])
    full_text = "\n\n".join(c["text"] for c in chunks)

    messages = [
        {"role": "system", "content": SUMMARIZE_SYSTEM.format(style=style)},
        {"role": "user", "content": f"Document text:\n{full_text}"},
    ]
    summary = llm_service.chat(messages)
    return SummarizeResponse(doc_id=doc_id, summary=summary, model_used=llm_service.model_name())


# ── Extraction ───────────────────────────────────────────────────────────────

def extract_fields(doc_id: str, fields: List[str]) -> ExtractResponse:
    query = " ".join(fields)
    chunks = embedding_service.search(query, top_k=8, doc_ids=[doc_id])
    full_text = "\n\n".join(c["text"] for c in chunks)

    fields_list = ", ".join(f'"{f}"' for f in fields)
    messages = [
        {"role": "system", "content": EXTRACT_SYSTEM},
        {"role": "user", "content": f"Fields to extract: [{fields_list}]\n\nDocument text:\n{full_text}"},
    ]
    raw = llm_service.chat(messages, json_mode=True)

    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        extracted = {"error": "Failed to parse LLM output", "raw": raw}

    return ExtractResponse(doc_id=doc_id, extracted=extracted, model_used=llm_service.model_name())


# ── Classification ───────────────────────────────────────────────────────────

def classify_document(doc_id: str, categories: List[str]) -> ClassifyResponse:
    chunks = embedding_service.search("document type purpose overview", top_k=6, doc_ids=[doc_id])
    full_text = "\n\n".join(c["text"] for c in chunks)

    cats = ", ".join(f'"{c}"' for c in categories)
    messages = [
        {"role": "system", "content": CLASSIFY_SYSTEM},
        {"role": "user", "content": f"Categories: [{cats}]\n\nDocument text:\n{full_text}"},
    ]
    raw = llm_service.chat(messages, json_mode=True)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"category": "unknown", "confidence": "low", "reasoning": "Parse error"}

    return ClassifyResponse(
        doc_id=doc_id,
        category=result.get("category", "unknown"),
        confidence=result.get("confidence", "low"),
        reasoning=result.get("reasoning", ""),
        model_used=llm_service.model_name(),
    )
