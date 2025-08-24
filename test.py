# Test Code for Data Analysis

# import os
# from pathlib import Path
# from io import BytesIO
# from src.document_analyzer.data_ingestion import DocumentHandler
# from src.document_analyzer.data_analysis import DocumentAnalyzer

# pdf_path = r"/Users/deepu/Downloads/study/LLMOps/document_rag/data/data_analysis/Data Science.pdf"

# class DummyFile:
#     def __init__(self, file_path):
#         self.name = Path(file_path).name
#         self._file_path = file_path

#     def getbuffer(self):
#         return open(self._file_path, "rb").read()

# def main():
#     try:
#         dummy_pdf = DummyFile(pdf_path)
#         handler = DocumentHandler(session_id="test_ingestion_session")
#         saved_path = handler.save_pdf(dummy_pdf)
#         text_content = handler.read_pdf(saved_path)

#         analyzer = DocumentAnalyzer()
#         analysis_result = analyzer.analyze_document(text_content)
#         print(f"Analysis Result: {analysis_result}")

#         for key, value in analysis_result.items():
#             print(f"{key}: {value}")

#     except Exception as e:
#         print(f"Test Error: {e}")

# if __name__ == "__main__":
#     main()

# Test Code for Data Comparsion

# import os
# import sys
# import io
# from pathlib import Path
# from src.document_compare.doc_ingestion import DocumentIngestion
# from src.document_compare.doc_compare import DocumentCompareLLM

# def load_fake_uploaded_file(file_path:Path):

#     return io.BytesIO(file_path.read_bytes())

# def test_compare_documents():

#     ref_path = Path("data/data_compare/CRT1.pdf")
#     act_path = Path("data/data_compare/CRT2.pdf")

#     class FakeUpload:
#         def __init__(self, file_path:Path):
#             self.name = file_path.name
#             self._buffer = file_path.read_bytes()

#         def getbuffer(self):
#             return self._buffer

#     comparator = DocumentIngestion()
#     ref_upload = FakeUpload(ref_path)
#     act_upload = FakeUpload(act_path)

#     ref_file, act_file = comparator.save_uploaded_file(ref_upload, act_upload)
#     combined_text = comparator.combine_documents()
#     comparator.clear_old_session(keep_latest=3)

#     llm_compare = DocumentCompareLLM()
#     result = llm_compare.compare_documents(combined_text[1000:])

#     print("==== Comparison Result ===")

#     print(f"Comparison Result: {result.head()}")
#     print(result.to_string(index=False))

# if __name__ == "__main__":
#     test_compare_documents()

# # Test Code for Single Document Chat

# import os
# import sys
# from src.single_document_chat.data_ingestion import SingleDocumentIngestor
# from src.single_document_chat.data_retrieval import ConversationalRAG
# from langchain_community.vectorstores import FAISS
# from utils.model_loader import ModelLoader
# from pathlib import Path

# FAISS_INDEX_PATH = Path("faiss_index")

# def test_single_document_chat(pdf_path, question:str):
#     try:
#         model_loader = ModelLoader()

#         if FAISS_INDEX_PATH.exists():
#             print("Loading exisintg FAISS Index")
#             embeddings = model_loader.load_embeddings()
#             vector_store = FAISS.load_local(folder_path = str(FAISS_INDEX_PATH), embeddings = embeddings, allow_dangerous_deserialization=True) #FAISS_INDEX_PATH, embeddings = embeddings, allow_dangerous_deserialization=True)
#             retreiver = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
#         else:
#             print("Creating new FAISS Index")
#             with open(pdf_path, "rb") as f:
#                 uploaded_files = [f]
#                 ingester = SingleDocumentIngestor()
#                 retreiver = ingester.ingest_file(uploaded_files)
#         print("Running Conversational RAG")
#         session_id = "test_chat_session"
#         rag = ConversationalRAG(
#             session_id=session_id,
#             retriever=retreiver
#         )
#         response = rag.invoke(question)
#         print(f"\nQuestion: {question}\nAnswer: {response}")
#         print(f"Response: {response}")

#     except Exception as e:
#         print(f"Test Error: {e}")

# if __name__ == "__main__":
#     pdf_path = r"data/single_document_chat/Data Science.pdf"
#     question = "What is central limit theorem?"
    
#     if not Path(pdf_path).exists():
#         print(f"PDF file not found at {pdf_path}")
#         sys.exit(1)

#     test_single_document_chat(pdf_path, question)


# Test Code for Multi Document Chat

import os
import sys
from src.multi_document_chat.data_ingestion import DocumentIngestor
from src.multi_document_chat.data_retrieval import ConversationalRAG
from utils.model_loader import ModelLoader
from pathlib import Path

FAISS_INDEX_PATH = Path("faiss_index")

def test_multi_document_chat():
    try:
        test_files = [
            "data/multi_doc_chat/Ant_Colony.ppt",
            "data/multi_doc_chat/CRT1.pdf",
            "data/multi_doc_chat/CRT2.pdf",
            "data/multi_doc_chat/PSO.ppt",
            # "data/multi_doc_chat/Data Science.pdf",
            "data/multi_doc_chat/TestMDC.docx",
        ]
        uploaded_files = []
        for file_path in test_files:
            if Path(file_path).exists():
                uploaded_files.append(open(file_path, "rb"))
            else:
                print(f"File not found at {file_path}")
                sys.exit(1)

        if not uploaded_files:
            print("No test files found.")
            sys.exit(1)
        
        Ingestor = DocumentIngestor()
        retreiver = Ingestor.ingest_file(uploaded_files)
        for f in uploaded_files:
            f.close()

        print("Running Conversational RAG")
        session_id = "test_chat_session"
        rag = ConversationalRAG(
            session_id=session_id,
            retriever=retreiver
        )
        question = "What is credit risk associated with exchange traded market"
        response = rag.invoke(question)
        print(f"\nQuestion: {question}\nAnswer: {response}")
        print(f"Response: {response}")

    except Exception as e:
        print(f"Test Error: {e}")

if __name__ == "__main__":

    test_multi_document_chat()

