import uuid
import os
import shutil
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Iterable, Optional, Dict, Any
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException

log = CustomLogger().get_logger(__name__)
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".ppt", ".txt"}

def _session_id(prefix="session"):
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

def save_uploaded_files(uploaded_files, target_dir):
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        saved: List[Path] = []
        for uf in uploaded_files:
            name = getattr(uf, "name", "file")
            ext = Path(name).suffix.lower()
            if ext not in SUPPORTED_EXTENSIONS:
                log.warning(f"Unsupported file type: {name}")
                continue

            unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
            out = target_dir / unique_filename
            with open(out, "wb") as f:
                if hasattr(uf, "read"):
                    f.write(uf.read())
                else:
                    f.write(uf.getbuffer())
            saved.append(out)
            log.info(f"File saved for ingestion: uploaded file: {name}, saved file: {out}")
        
        return saved

    except Exception as e:
        log.error(f"Error saving uploaded file: {str(e)}")
        raise CustomException(f"Failed to save uploaded file:", e) from e