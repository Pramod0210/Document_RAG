import json
import uuid
import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Iterable, Optional, Dict, Any

import fitz
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstores import FAISS

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException

log = CustomLogger().get_logger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".ppt", ".txt"}

def load_documents(paths):
    docs: List[Document] = []
    try:
        for p in paths:
            ext = p.suffix.lower()
            if ext == ".pdf":
                loader = PyPDFLoader(str(p))
            elif ext == ".docx":
                loader = Docx2txtLoader(str(p))
            elif ext == ".txt":
                loader = TextLoader(str(p), encoding="utf8")
            else:
                log.warning(f"Unsupported file type: {p}")
                continue
            docs.extend(loader.load())
        log.info(f"Loaded {len(docs)} documents.")
        return docs

    except Exception as e:
        log.error(f"Error loading documents: {str(e)}")
        raise CustomException(f"Failed to load documents:", e) from e
    

def concat_for_analysis(docs):
    parts = []
    for doc in docs:
        src = doc.metadata.get("source") or doc.metadata.get("file_path") or "unknown"
        parts.append(f"\n---SOURCE: {src} ---\n{doc.page_content}")
    return "\n".join(parts)

def concact_for_comparison(ref_docs, act_docs):
    left = concat_for_analysis(ref_docs)
    right = concat_for_analysis(act_docs)
    return f"<<REREFERENCE_DOCUMENTSS>>\n{left}\n\n<<ACTUAL_DOCUMENTS>>\n{right}"