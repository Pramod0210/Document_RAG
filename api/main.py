from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from typing import Dict, Optional, List, Any

from src.document_ingestion.data_ingestion import (
    DocumentHandler,
    DocumentComparator,
    FaissManager,
    ChatIngestor
)
from src.document_analyzer.data_analysis import DocumentAnalyzer
from src.document_compare.doc_compare import DocumentCompareLLM
from src.document_chat.retrieval import ConversationalRAG

UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")
FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")

app = FastAPI(title="Document RAG", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../static"), name="static")

templates = Jinja2Templates(directory="../templates")
class FastAPIFileAdaptor:
    def __init__(self, uf:UploadFile):
        self._uf = uf
        self.name = uf.filename
    
    def getbuffer(self):
        self._uf.file.seek(0)
        return self._uf.file.read()
    
def _read_pdf_via_handler(handler: DocumentHandler, path):
    try:
        if hasattr(handler, "read_pdf"):
            return handler.read_pdf(path)
        if hasattr(handler, "read_"):
            return handler.read_(path)
        raise RuntimeError("Failed to read PDF")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read PDF: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health", response_class=JSONResponse)
async def health():
    return {"status": "ok", "service":"document-rag"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        dh = DocumentHandler()
        saved_path = dh.save_pdf(FastAPIFileAdaptor(file))
        text = _read_pdf_via_handler(dh, saved_path)
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_document(text)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: + {str(e)}")
    
@app.post("/compare")
async def compare(reference: UploadFile = File(...), actual: UploadFile = File(...)):
    try:
        dc = DocumentComparator()
        ref_path, act_path = dc.save_uploaded_file(FastAPIFileAdaptor(reference), FastAPIFileAdaptor(actual))
        _ = ref_path, act_path
        combined_text = dc.combine_documents()
        compare = DocumentCompareLLM()
        result = compare.compare_documents(combined_text)
        return {"rows": result.to_dict(orient="records"), "session_id": dc.session_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: + {str(e)}")

@app.post("/chat/index")
async def chat_build_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(False),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),
):
    try:
        wrapped = [FastAPIFileAdaptor(f) for f in files]
        ci = ChatIngestor(
            temp_base = UPLOAD_BASE,
            faiss_base = FAISS_BASE,
            use_session_dirs = use_session_dirs,
            session_id = session_id or None,
        )
        ci.built_retriever(wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k)
        return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: + {str(e)}")

@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    use_session_dirs: bool = Form(False),
    session_id: Optional[str] = Form(None),
    k: int = Form(5),
):
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required when using session directories.")
        
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, detail=f"Index not found. {index_dir}")
        
        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir)

        response = rag.invoke(question, chat_history=[])
        return {"answer": response,
                "session_id": session_id,
                "k": k,
                "engine": "LCEL-RAG"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: + {str(e)}")


# Fastapi Command
# uvicorn main:app --reload
