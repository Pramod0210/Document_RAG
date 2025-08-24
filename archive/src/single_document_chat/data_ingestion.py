import sys
import os
import uuid
from datetime import datetime
from pathlib import Path
from utils.model_loader import ModelLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException


class SingleDocumentIngestor:
    def __init__(self, data_dir="data/single_document_chat", faiss_dir = "faiss_index"):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)
            self.model_loader = ModelLoader()
            self.log.info(f"Initialized SingleDocumentIngestor with data directory: {self.data_dir} and FAISS directory: {self.faiss_dir}")

        except Exception as e:
            self.log.error(f"Error initializing SingleDocumentIngestor: {str(e)}")
            raise CustomException(f"Failed to initialize SingleDocumentIngestor:", sys)
        
    def ingest_file(self, uploaded_files):
        
        try:
            documents = []

            for document in uploaded_files:
                unique_filename = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = self.data_dir/unique_filename

                with open(temp_path, "wb") as f:
                    f.write(document.read())
                
                self.log.info(f"Ingesting file: {document.name}")

                loader = PyPDFLoader(temp_path)
                docs = loader.load()
                documents.extend(docs)

                self.log.info(f"Ingested file: {document.name}")

            return self._create_retriever(documents)

        except Exception as e:
            self.log.error(f"Error ingesting file: {str(e)}")
            raise CustomException(f"Failed to ingest file: ", sys)
        
    def _create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
            chunks = splitter.split_documents(documents)
            self.log.info(f"Created splitter with {len(chunks)} chunks")

            embedding = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(chunks, embedding)

            vectorstore.save_local(str(self.faiss_dir))
            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

            self.log.info("Retriever created successfully")
            return retriever

        except Exception as e:
            self.log.error(f"Error creating retriever: {str(e)}")
            raise CustomException(f"Failed to create retriever: ", sys)

