"""Q&A, summarize, extract, and classify endpoints."""
from fastapi import APIRouter, HTTPException
from backend.models import (
    QueryRequest, QueryResponse,
    SummarizeRequest, SummarizeResponse,
    ExtractRequest, ExtractResponse,
    ClassifyRequest, ClassifyResponse,
)
from backend.services import rag_service
from backend.services.document_service import get_document_meta

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("/ask", response_model=QueryResponse)
def ask_question(req: QueryRequest):
    """Answer a question using RAG over indexed documents."""
    return rag_service.answer_question(req.question, req.doc_ids, req.top_k or 5)


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    """Summarize a specific document."""
    if not get_document_meta(req.doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return rag_service.summarize_document(req.doc_id, req.style)


@router.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest):
    """Extract structured fields from a document."""
    if not get_document_meta(req.doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return rag_service.extract_fields(req.doc_id, req.fields)


@router.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    """Classify a document into one of the provided categories."""
    if not get_document_meta(req.doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return rag_service.classify_document(req.doc_id, req.categories)
