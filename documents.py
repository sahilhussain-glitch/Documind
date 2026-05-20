"""Document upload, list, and delete endpoints."""
import os
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.services.document_service import (
    process_document, list_documents, delete_document, get_document_meta
)
from backend.services.embedding_service import index_document, remove_document

router = APIRouter(prefix="/api/documents", tags=["documents"])
settings = get_settings()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and index a PDF, DOCX, or TXT file."""
    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".docx", ".doc", ".txt"):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_file_size_mb}MB limit")

    # Save file temporarily
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)
    tmp_path = upload_dir / file.filename
    with open(tmp_path, "wb") as f:
        f.write(content)

    try:
        doc_id, chunks = process_document(str(tmp_path), file.filename)
        index_document(doc_id, chunks)
    except Exception as e:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))

    meta = get_document_meta(doc_id)
    return {"message": "Document uploaded and indexed successfully", "document": meta}


@router.get("")
def list_all_documents():
    """List all indexed documents."""
    return {"documents": list_documents()}


@router.delete("/{doc_id}")
def delete_doc(doc_id: str):
    """Remove a document from the index."""
    if not delete_document(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    remove_document(doc_id)
    return {"message": f"Document {doc_id} deleted"}
