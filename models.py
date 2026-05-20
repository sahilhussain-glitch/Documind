from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentMeta(BaseModel):
    doc_id: str
    filename: str
    num_chunks: int
    file_type: str
    uploaded_at: datetime


class QueryRequest(BaseModel):
    question: str
    doc_ids: Optional[List[str]] = None   # None = search all docs
    top_k: Optional[int] = 5


class SummarizeRequest(BaseModel):
    doc_id: str
    style: str = "concise"               # concise | detailed | bullets


class ExtractRequest(BaseModel):
    doc_id: str
    fields: List[str]                    # e.g. ["date", "parties", "amount"]


class ClassifyRequest(BaseModel):
    doc_id: str
    categories: List[str]               # e.g. ["invoice", "contract", "report"]


class Source(BaseModel):
    doc_id: str
    filename: str
    chunk_index: int
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    model_used: str


class SummarizeResponse(BaseModel):
    doc_id: str
    summary: str
    model_used: str


class ExtractResponse(BaseModel):
    doc_id: str
    extracted: Dict[str, Any]
    model_used: str


class ClassifyResponse(BaseModel):
    doc_id: str
    category: str
    confidence: str
    reasoning: str
    model_used: str
