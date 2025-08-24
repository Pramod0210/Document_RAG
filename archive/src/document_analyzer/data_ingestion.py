import os
import sys
import fitz
import uuid
from datetime import datetime
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException


class DocumentHandler:
    def __init__(self, data_dir=None, session_id=None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = data_dir or os.getenv(
                "DATA_DIR", 
                os.path.join(os.getcwd(), "data", "data_analysis")
            )
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_path = os.path.join(self.data_dir, self.session_id)
            os.makedirs(self.session_path, exist_ok=True)
            self.log.info(f"DocumentLoader initialized with session ID: {self.session_id} and data directory: {self.data_dir}")
        except Exception as e:
            self.log.error(f"Error initializing DocumentLoader: {str(e)}")
            raise CustomException(f"Failed to initialize DocumentLoader: {str(e)}", sys)
    
    def save_pdf(self, uploaded_file_name):
        try:
            filename = os.path.basename(uploaded_file_name.name)

            if not filename.lower().endswith('.pdf'):
                self.log.error("Uploaded file is not a PDF.")
                raise CustomException("Uploaded file is not a PDF.", sys)
            
            save_path = os.path.join(self.session_path, filename)
            with open(save_path, "wb") as f:
                f.write(uploaded_file_name.getbuffer())
            
            self.log.info(f"PDF saved", filename=filename, save_path= save_path, session_id=self.session_id)
            return save_path
        
        except Exception as e:
            self.log.error(f"Error saving PDF: {str(e)}")
            raise CustomException(f"Failed to save PDF: {str(e)}", sys)

    def read_pdf(self, pdf_path):
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc, start=1):
                    text_chunks.append(f"\n--- Page {page_num} ---\n{page.get_text()}")
            text = "\n".join(text_chunks)
            self.log.info(f"PDF read successfully", pdf_path=pdf_path, num_pages=len(text_chunks))
            return text
        except Exception as e:
            self.log.error(f"Error reading PDF: {str(e)}")
            raise CustomException(f"Failed to read PDF: {str(e)}", sys)
    

if __name__ == "__main__":
    from pathlib import Path
    from io import BytesIO

    pdf_path = r"/Users/deepu/Downloads/study/LLMOps/document_rag/data/data_analysis/Data Science.pdf"

    class DummyFile:
        def __init__(self, file_path):
            self.name = Path(file_path).name
            self._file_path = file_path

        def getbuffer(self):
            return open(self._file_path, "rb").read()

    dummy_pdf = DummyFile(pdf_path)

    handler = DocumentHandler(session_id="test_session")
    try:
        saved_path = handler.save_pdf(dummy_pdf)
        content = handler.read_pdf(saved_path)
        print(f"Content of the PDF:\n{content[:500]}...")  #
        # print(saved_path)
        # print(f"PDF saved at: {saved_path}")
    except Exception as e:
        print(f"Error: {e}")

