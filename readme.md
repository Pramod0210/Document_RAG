# Document RAG

An end-to-end **document intelligence platform** that lets you chat with your documents, extract structured metadata, and diff two versions of a document — powered by a LangChain **RAG (Retrieval-Augmented Generation)** pipeline, served through a **FastAPI** backend with a built-in web UI, containerized with Docker, and deployed to **AWS ECS Fargate** through a GitHub Actions CI/CD pipeline.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-0.3-1C3C3C?logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/FAISS-vector%20store-4B8BBE" alt="FAISS">
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/AWS-ECS%20Fargate-FF9900?logo=amazonaws&logoColor=white" alt="AWS ECS Fargate">
</p>

---

## Why this project

Most RAG demos stop at a notebook. This one is built the way a production service would be:

- **Pluggable model layer** — swap between Google Gemini and Groq with a single env var, no code changes.
- **Incremental, deduplicated indexing** — documents are fingerprinted (SHA-256 / source+row id) so re-ingesting the same file never duplicates vectors.
- **Session isolation** — each chat session can get its own upload directory and FAISS index.
- **Structured LLM output** — analysis and comparison responses are parsed into Pydantic schemas with an output-fixing parser, so the API returns reliable JSON instead of free text.
- **Operational plumbing** — structured JSON logging (`structlog`), a custom exception type carrying file/line context, unit tests, and a full CI/CD path to AWS.

---

## Features

| Feature | What it does | Endpoint |
|---|---|---|
| **Conversational RAG** | Build a FAISS index from uploaded documents and ask multi-turn questions against it, with history-aware query rewriting | `POST /chat/index`, `POST /chat/query` |
| **Document Analysis** | Extracts structured metadata — title, author, summary, language, page count, sentiment tone — as validated JSON | `POST /analyze` |
| **Document Comparison** | Page-by-page LLM diff of a reference vs. an actual document, returned as tabular rows | `POST /compare` |
| **Web UI** | Jinja2 + vanilla JS frontend for all three flows | `GET /` |
| **Health / Docs** | Health probe for ECS target checks, plus auto-generated OpenAPI docs | `GET /health`, `GET /docs` |

Supported file types: `.pdf`, `.docx`, `.txt`, `.md`, `.ppt`

---

## Architecture

```
                     ┌──────────────────────────────┐
   Browser  ────────▶│  FastAPI  (api/main.py)      │
   / REST            │  UI · /analyze · /compare    │
                     │  /chat/index · /chat/query   │
                     └───────────────┬──────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
      ┌───────────────┐     ┌────────────────┐     ┌────────────────┐
      │ DocumentHandler│    │ DocumentAnalyzer│    │ConversationalRAG│
      │ DocumentCompar.│    │ DocumentCompare │    │  (LCEL chain)   │
      │ ChatIngestor   │    │      LLM        │    └───────┬─────────┘
      └───────┬───────┘     └────────┬───────┘             │
              │                      │                     │
              ▼                      ▼                     ▼
      ┌───────────────┐     ┌────────────────┐     ┌────────────────┐
      │ Text splitter │     │  ModelLoader   │◀────│ FAISS retriever│
      │ + FaissManager│────▶│ Gemini / Groq  │     │    (top-k=5)   │
      │  (dedup meta) │     │ + embeddings   │     └────────────────┘
      └───────────────┘     └────────────────┘
```

**RAG query flow:** question + chat history → *contextualize* prompt rewrites it into a standalone question → FAISS similarity search (`k=5`) → retrieved chunks formatted into the *context QA* prompt → LLM → `StrOutputParser` → answer. The whole thing is composed with LangChain Expression Language (LCEL) in [retrieval.py](src/document_chat/retrieval.py).

---

## Tech Stack

| Layer | Choice |
|---|---|
| API | FastAPI, Uvicorn, Pydantic, Jinja2 |
| RAG / LLM | LangChain (LCEL), Google Gemini 2.0 Flash, Groq DeepSeek-R1-Distill-Llama-70B |
| Embeddings | Google `text-embedding-004` |
| Vector store | FAISS (local, persisted per session) |
| Parsing | PyMuPDF, pypdf, docx2txt, `RecursiveCharacterTextSplitter` |
| Observability | structlog (JSON logs), custom exception with traceback context |
| Testing | pytest, FastAPI `TestClient` |
| Infra | Docker, AWS ECR, ECS Fargate, Secrets Manager, CloudWatch, CloudFormation |
| CI/CD | GitHub Actions (tests → build & push image → deploy) |

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/Pramod0210/Document_RAG.git
cd Document_RAG

python -m venv myvenv && source myvenv/bin/activate   # Windows: myvenv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key

LLM_PROVIDER=google        # 'google' or 'groq' — selects the block in config/config.yaml
ENV=local                  # 'production' skips .env loading and reads ECS secrets
UPLOAD_BASE=data           # where uploaded files are saved
FAISS_BASE=faiss_index     # where FAISS indexes are persisted
```

Model names, temperature, token limits and retriever `top_k` live in [config/config.yaml](config/config.yaml) — change models there without touching code.

### 3. Run

```bash
uvicorn api.main:app --reload
```

| | |
|---|---|
| Web UI | http://localhost:8000/ |
| Swagger docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

### 4. Run with Docker

```bash
docker build -t document-rag .
docker run -p 8080:8080 --env-file .env document-rag
# → http://localhost:8080
```

---

## API Reference

<details>
<summary><b>POST /chat/index</b> — build a vector index from documents</summary>

```bash
curl -X POST http://localhost:8000/chat/index \
  -F "files=@doc1.pdf" -F "files=@doc2.pdf" \
  -F "use_session_dirs=true" \
  -F "chunk_size=1000" -F "chunk_overlap=200" -F "k=5"
```
```json
{ "session_id": "session_20250302_150142_ab12cd34", "k": 5, "use_session_dirs": true }
```
</details>

<details>
<summary><b>POST /chat/query</b> — ask a question against an index</summary>

```bash
curl -X POST http://localhost:8000/chat/query \
  -F "question=What is the termination clause?" \
  -F "session_id=session_20250302_150142_ab12cd34" \
  -F "use_session_dirs=true" -F "k=5"
```
```json
{ "answer": "...", "session_id": "...", "k": 5, "engine": "LCEL-RAG" }
```
</details>

<details>
<summary><b>POST /analyze</b> — structured metadata extraction</summary>

```bash
curl -X POST http://localhost:8000/analyze -F "file=@report.pdf"
```
```json
{
  "Summary": ["..."], "Title": "...", "Author": "...",
  "DateCreated": "...", "LastDateModified": "...", "Published": "...",
  "Language": "English", "PageCount": 12, "SentimentTone": "Neutral"
}
```
</details>

<details>
<summary><b>POST /compare</b> — page-wise document diff</summary>

```bash
curl -X POST http://localhost:8000/compare \
  -F "reference=@v1.pdf" -F "actual=@v2.pdf"
```
```json
{ "rows": [{ "page": "1", "changes": "NO CHANGES" },
            { "page": "2", "changes": "Payment terms changed from 30 to 45 days" }],
  "session_id": "..." }
```
</details>

---

## Project Structure

```
Document_RAG/
├── api/
│   └── main.py                       # FastAPI app, routes, UploadFile adapter
├── src/
│   ├── document_ingestion/
│   │   └── data_ingestion.py         # DocumentHandler, DocumentComparator,
│   │                                 # FaissManager (dedup), ChatIngestor
│   ├── document_analyzer/
│   │   └── data_analysis.py          # DocumentAnalyzer  → Metadata schema
│   ├── document_compare/
│   │   └── doc_compare.py            # DocumentCompareLLM → DataFrame of changes
│   └── document_chat/
│       └── retrieval.py              # ConversationalRAG (LCEL chain + FAISS)
├── utils/
│   ├── model_loader.py               # ApiKeyManager + ModelLoader (Gemini/Groq)
│   ├── config_loader.py              # YAML config loader
│   ├── document_ops.py               # multi-format loaders & text concat helpers
│   └── file_io.py                    # session ids, upload persistence
├── prompt/prompt_library.py          # PROMPT_REGISTRY — analysis, compare, RAG prompts
├── model/models.py                   # Pydantic schemas & PromptType enum
├── logger/custom_logger.py           # structlog JSON logging (console + file)
├── exception/custom_exception.py     # exception with file/line traceback context
├── config/config.yaml                # models, embeddings, retriever settings
├── templates/ · static/              # Jinja2 UI + CSS
├── tests/test_unit_cases.py          # pytest + FastAPI TestClient
├── infrastructure/document-rag-cf.yaml  # CloudFormation: VPC, ECR, ECS, IAM, logs
├── .github/workflows/                # ci.yaml (tests) → aws.yaml (build & deploy)
├── Dockerfile
└── requirements.txt
```

---

## Deployment (AWS ECS Fargate)

The pipeline in [.github/workflows/](.github/workflows/) runs tests on every push; on a green build against `main` it builds the image, pushes it to **ECR**, renders the ECS task definition, and rolls out a new revision to the **ECS Fargate** service — waiting for service stability before reporting success.

```
push → ci.yaml (pytest) → aws.yaml → docker build → ECR → ECS task definition → Fargate service
```

Setup checklist:

1. Create an IAM user and store `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` as GitHub repository secrets.
2. Attach the policies in [inline_policy.json](inline_policy.json) (ECR + ECS + Secrets Manager permissions).
3. Store `GOOGLE_API_KEY` / `GROQ_API_KEY` in **AWS Secrets Manager**; the container reads them from the `llm_api_keys` JSON secret at boot.
4. Provision ECR, the ECS cluster and networking — either manually or with [infrastructure/document-rag-cf.yaml](infrastructure/document-rag-cf.yaml).
5. Open inbound TCP **8080** on the service security group.
6. Reach the app at `http://<task-public-ip>:8080`; logs stream to **CloudWatch** under the task's log group.

Full step-by-step notes: [deployment_steps.txt](deployment_steps.txt).

---

## Testing

```bash
pytest tests/
```

---

## Roadmap

- [ ] Persist chat history per session (currently each query is stateless at the API boundary)
- [ ] Hybrid retrieval (BM25 + dense) and a reranking stage
- [ ] Streaming token responses over SSE
- [ ] Retrieval evaluation harness (faithfulness / answer relevance)
- [ ] Move FAISS to a managed vector store for horizontal scaling

---

## Author

**Pramod** — [GitHub](https://github.com/Pramod0210)

## License

Released under the MIT License.
