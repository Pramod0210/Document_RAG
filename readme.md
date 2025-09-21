# Document RAG System

A FastAPI-based Retrieval-Augmented Generation (RAG) system for document ingestion, chat, and analysis. Supports multiple document formats, table/image extraction, evaluation matrix (DeepEval), and LangChain in-memory caching.

---

## Features

- **Document Upload:** Supports `.pdf`, `.docx`, `.md`, `.ppt`, `.txt`, `.xlsx`, `.csv`, and SQL DBs.
- **Table & Image Extraction:** Handles tabular and image data from documents.
- **Chat & Retrieval:** Query uploaded documents using conversational AI.
- **Evaluation Matrix:** Integrated with DeepEval for answer quality assessment.
- **LangChain InMemoryCache:** Speeds up repeated LLM queries.
- **Authentication:** Simple login portal.
- **CI/CD:** GitHub Actions for testing and AWS ECS deployment.
- **Secrets Management:** Uses AWS Secrets Manager for API keys.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Pramod0210/Document_RAG.git
cd Document_RAG
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
uvicorn api.main:app --reload --port 8080
```

### 4. Docker Usage

Build the image:
```bash
docker build -t document-rag-system .
```

Run the container:
```bash
docker run -d -p 8092:8000 --name docapp document-rag-system
```

---

## API Endpoints

- `POST /chat/index` — Upload and index documents.
- `POST /chat/query` — Query documents with natural language.
- `POST /eval` — Evaluate answers using DeepEval.
- `GET /login` — Login portal.

---

## Testing

Unit tests are in `tests/test_unit_cases.py`.  
Run tests before and after each commit:

```bash
pytest tests/
```

---

## AWS & Secrets

- Store API keys in AWS Secrets Manager as `llm_api_keys`.
- ECS task definition injects secrets as environment variables.

---

## Notes

- Make sure sample files for testing are in the `tests/` directory.
- Adjust endpoints and payloads as needed for your use case.

---

## License

MIT