import os
import sys
from pathlib import Path
import uuid
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredPowerPointLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException

class DocumentIngestor:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".ppt", ".txt"}
    def __init__(self, temp_dir = "data/multi_doc_chat", faiss_dir = "faiss_index", session_id = None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.model_loader = ModelLoader()
            self.log.info("Initialized MultiDocIngestor")
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_path = self.temp_dir / self.session_id
            self.session_path.mkdir(parents=True, exist_ok=True)
            self.faiss_session_path = self.faiss_dir / self.session_id
            self.faiss_session_path.mkdir(parents=True, exist_ok=True)
            self.model_loader = ModelLoader()
            self.log.info(f"MultiDocIngestor initialized with session ID: {self.session_id} and data directory: {self.session_path}")

        except Exception as e:
            self.log.error(f"Error initializing MultiDocIngestor: {str(e)}")
            raise CustomException(f"Failed to initialize MultiDocIngestor: {str(e)}", sys)

    def ingest_file(self, uploaded_files):
        try:
            documents = []
        
            for uploaded_file in uploaded_files:
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in self.SUPPORTED_EXTENSIONS:
                    self.log.warning(f"Unsupported file type: {uploaded_file.filename}")
                    continue

                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
                temp_path = self.session_path/unique_filename

                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                self.log.info(f"Ingesting file:")

                if ext == ".pdf":
                    loader = PyPDFLoader(temp_path)
                elif ext == ".docx":
                    loader = Docx2txtLoader(temp_path)
                elif ext == ".txt":
                    loader = TextLoader(temp_path)
                else:
                    self.log.warning(f"Unsupported file type: {uploaded_file}")
                    continue
                # elif ext == ".ppt":
                #     loader = UnstructuredPowerPointLoader(temp_path)

                docs = loader.load()
                documents.extend(docs)

            if not documents:
                raise CustomException(f"Failed to ingest file: ", sys)

            self.log.info(f"Ingested files:")

            return self._create_retriever(documents)

        except Exception as e:
            self.log.error(f"Error ingesting file: {str(e)}")
            raise CustomException(f"Failed to ingest file: ", sys)

    def _create_retriever(self, documents):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
            chunks = text_splitter.split_documents(documents)

            self.log.info(f"Created splitter with {len(chunks)} chunks")

            embeddings = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(chunks, embeddings)

            vectorstore.save_local(str(self.faiss_session_path))
            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self.log.info("Retriever created successfully")
            return retriever
        
        except Exception as e:
            self.log.error(f"Error creating retriever: {str(e)}")
            raise CustomException(f"Failed to create retriever: ", sys)