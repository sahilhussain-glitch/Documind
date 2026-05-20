"""DocuMind — FastAPI entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import documents, query

app = FastAPI(
    title="DocuMind API",
    description="LLM-Powered Document Intelligence Platform using RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(query.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "DocuMind"}
