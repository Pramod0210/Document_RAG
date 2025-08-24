import sys
import fitz
from pathlib import Path
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException
import os
import uuid
from datetime import datetime

class DocumentIngestion:
    def __init__(self, base_dir="data/data_compare", session_id=None):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        # self.base_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.log.info(f"DocumentIngestion initialized with session ID: {self.session_id} and data directory: {self.session_path}")

    def save_uploaded_file(self, reference_file, actual_file):
        try:
            # self.delete_exisiting_files()
            self.log.info("Existing file deleted successfully")

            ref_path = self.session_path / reference_file.name
            act_path = self.session_path / actual_file.name
            if not reference_file.name.lower().endswith('.pdf') or not actual_file.name.lower().endswith('.pdf'):
                self.log.error("Files are not PDF.")
                raise CustomException("Files are not PDF.", sys)
            
            with open(ref_path, "wb") as f:
                f.write(reference_file.getbuffer())
            
            with open(act_path, "wb") as f:
                f.write(actual_file.getbuffer())
            
            self.log.info(f"Files saved successfully", reference_file=reference_file.name, actual_file=actual_file.name)
            return ref_path, act_path
            
        except Exception as e:
            self.log.error(f"Error saving uploaded file: {str(e)}")
            raise CustomException(f"Failed to save uploaded file: {str(e)}", sys)

    def read_pdf(self, pdf_path):
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted and cannot be read. {pdf_path.name}")
                
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text.strip():
                        all_text.append(f"\n--- Page {page_num+1} ---\n{page_text}")
                self.log.info(f"PDF read successfully", file=str(pdf_path), pages=len(all_text))

                # all_text = "\n".join(all_text) 
                return "\n".join(all_text) 
            
        except Exception as e:
            self.log.error(f"Error reading PDF: {str(e)}")
            raise CustomException(f"Failed to read PDF: {str(e)}", sys)

    
    def combine_documents(self):
        try:
            # content_dict = {}
            doc_parts = []

            for filename in sorted(self.session_path.iterdir()):
                if filename.is_file() and filename.suffix.lower() == '.pdf':
                    text = self.read_pdf(filename)
                    # content_dict[filename.name] = text
                    doc_parts.append(f"Document: {filename.name}\n{text}")
                
            # for filename, content in content_dict.items():
            #     doc_parts.append(f"Document: {filename}\n{content}")
            
            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents combined successfully.", count=len(doc_parts))
            return combined_text
 
        except Exception as e:
            self.log.error(f"Error combining documents: {str(e)}")
            raise CustomException(f"Failed to combine documents: {str(e)}", sys)
        
    def clear_old_session(self, keep_latest=3):
        try:
            session_folder = sorted([f for f in self.base_dir.iterdir() if f.is_dir()],
                                    reverse=True)
            
            for folder in session_folder[keep_latest:]:
                for file in folder.iterdir():
                    file.unlink()
                folder.rmdir()
            self.log.info("Old sessions cleared successfully.")
        except Exception as e:
            self.log.error(f"Error clearing session: {str(e)}")
            raise CustomException(f"Failed to clear session: {str(e)}", sys)