# Document RAG

A powerful document intelligence platform with **RAG-based chat**, **document analysis**, and **document comparison** — all served via a FastAPI backend with a built-in web UI.

---

##  Features

| Feature | Description |
|---|---|
| **Document Analysis** | Upload a PDF and extract structured insights automatically |
| **Document Comparison** | Compare two PDFs side-by-side with LLM-powered diff analysis |
| **Conversational Chat** | Build a FAISS vector index from PDFs and chat with your documents |
| **Web UI** | Built-in HTML/Jinja2 frontend served at `/` |
| **REST API** | Full JSON API for programmatic access |

---

## Requirements

- Python >= 3.10
- FastAPI, Uvicorn
- FAISS
- LangChain (for RAG pipeline)
- An `.env` file for configuration

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/document-rag.git
cd document-rag

# Install dependencies
pip install -e .
```

---

## Configuration

Create a `.env` file in the project root:

```env
UPLOAD_BASE=data          # Directory where uploaded PDFs are saved
FAISS_BASE=faiss_index    # Directory where FAISS indexes are stored
```

---

## Running the Server

```bash
uvicorn api.main:app --reload
```

- **Web UI** → `http://localhost:8000/`
- **Swagger Docs** → `http://localhost:8000/docs`
- **Health Check** → `http://localhost:8000/health`

---

## Project Structure

```
document-rag/
├── api/
│   └── main.py                        # FastAPI app & all routes
├── src/
│   ├── document_ingestion/
│   │   └── data_ingestion.py          # DocumentHandler, DocumentComparator, FaissManager, ChatIngestor
│   ├── document_analyzer/
│   │   └── data_analysis.py           # DocumentAnalyzer
│   ├── document_compare/
│   │   └── doc_compare.py             # DocumentCompareLLM
│   └── document_chat/
│       └── retrieval.py               # ConversationalRAG
├── static/                            # Frontend static assets
├── templates/
│   └── index.html                     # Jinja2 web UI template
├── data/                              # Uploaded PDFs (auto-created)
├── faiss_index/                       # FAISS indexes (auto-created)
├── .env
└── README.md
```

---

## Typical Workflow

**Document Chat (multi-turn):**
```
1. POST /chat/index  →  Upload PDFs, receive a session_id
2. POST /chat/query  →  Ask questions using that session_id
```

**One-shot tasks:**
```
POST /analyze  →  Get structured analysis of a single PDF
POST /compare  →  Get an LLM-generated comparison table of two PDFs
```

---

## License

Proprietary — All rights reserved.
