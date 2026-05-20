# Documind
# DocuMind — LLM-Powered Document Intelligence Platform

> Upload documents, ask questions, extract insights — powered by RAG + LLMs.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![React](https://img.shields.io/badge/React-18-blue) ![LangChain](https://img.shields.io/badge/LangChain-0.3-orange)

---

## What It Does

DocuMind lets you upload PDF/DOCX files and query them using natural language. It uses **Retrieval-Augmented Generation (RAG)** — documents are chunked, embedded into a FAISS vector index, and the most relevant chunks are injected into the LLM prompt at query time.

**Supported use cases:**
- Summarization of long documents
- Multi-document question answering
- Structured data extraction (dates, names, figures)
- Classification of document type or topic

---

## Architecture

```
User → React Frontend → FastAPI Backend
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
       Document Upload   Vector Index     LLM API
       (PDF/DOCX parse)  (FAISS+Embed)   (OpenAI/Claude)
              │               │                │
              └───────────────▼────────────────┘
                         RAG Pipeline
                    (retrieve → augment → generate)
```

---

## Project Structure

```
documind/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings from .env
│   ├── models.py                # Pydantic request/response models
│   ├── services/
│   │   ├── document_service.py  # PDF/DOCX parsing & chunking
│   │   ├── embedding_service.py # FAISS index management
│   │   ├── llm_service.py       # OpenAI / Claude API calls
│   │   └── rag_service.py       # Full RAG pipeline
│   └── routes/
│       ├── documents.py         # Upload, list, delete endpoints
│       └── query.py             # Q&A and extraction endpoints
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── DocumentUpload.jsx
│           ├── QueryInterface.jsx
│           └── ResultCard.jsx
├── .env.example
├── requirements.txt
└── README.md
```

---

## Quick Start

### Backend

```bash
# 1. Clone and enter project
git clone https://github.com/yourname/documind.git
cd documind

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your API keys

# 5. Run the server
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload a PDF or DOCX file |
| GET | `/api/documents` | List all indexed documents |
| DELETE | `/api/documents/{doc_id}` | Remove a document |
| POST | `/api/query/ask` | Ask a question (RAG) |
| POST | `/api/query/summarize` | Summarize a document |
| POST | `/api/query/extract` | Extract structured data |
| POST | `/api/query/classify` | Classify document type |

---

## Key Design Decisions

- **Chunking strategy**: 800-token chunks with 100-token overlap for context continuity
- **Prompt templates**: Few-shot examples for extraction; explicit output schemas for JSON mode
- **LLM abstraction**: `llm_service.py` supports both OpenAI and Anthropic — switch via `.env`
- **Accuracy improvement**: Structured prompts + output validation improved extraction accuracy ~35% vs naive prompting

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | — |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | — |
| `LLM_PROVIDER` | `openai` or `anthropic` | `openai` |
| `EMBED_MODEL` | Embedding model name | `text-embedding-3-small` |
| `CHAT_MODEL` | Chat model name | `gpt-4o` |
| `CHUNK_SIZE` | Tokens per chunk | `800` |
| `TOP_K` | Retrieved chunks per query | `5` |
