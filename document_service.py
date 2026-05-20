"""Handles document parsing (PDF/DOCX) and text chunking."""
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from docx import Document as DocxDocument

from backend.config import get_settings
from backend.models import DocumentMeta

settings = get_settings()

# In-memory registry (swap for a database in production)
_document_registry: dict[str, DocumentMeta] = {}


def parse_pdf(filepath: str) -> str:
    """Extract raw text from a PDF file."""
    reader = PdfReader(filepath)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def parse_docx(filepath: str) -> str:
    """Extract raw text from a DOCX file."""
    doc = DocxDocument(filepath)
    return "\n\n".join(para.text for para in doc.paragraphs if para.text.strip())


def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def process_document(filepath: str, filename: str) -> Tuple[str, List[str]]:
    """
    Parse and chunk a document.
    Returns (doc_id, list_of_chunks).
    """
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        raw_text = parse_pdf(filepath)
        file_type = "pdf"
    elif ext in (".docx", ".doc"):
        raw_text = parse_docx(filepath)
        file_type = "docx"
    elif ext == ".txt":
        with open(filepath, encoding="utf-8") as f:
            raw_text = f.read()
        file_type = "txt"
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    chunks = chunk_text(raw_text)
    doc_id = str(uuid.uuid4())

    meta = DocumentMeta(
        doc_id=doc_id,
        filename=filename,
        num_chunks=len(chunks),
        file_type=file_type,
        uploaded_at=datetime.utcnow(),
    )
    _document_registry[doc_id] = meta
    return doc_id, chunks


def get_document_meta(doc_id: str) -> DocumentMeta | None:
    return _document_registry.get(doc_id)


def list_documents() -> List[DocumentMeta]:
    return list(_document_registry.values())


def delete_document(doc_id: str) -> bool:
    if doc_id in _document_registry:
        del _document_registry[doc_id]
        return True
    return False
