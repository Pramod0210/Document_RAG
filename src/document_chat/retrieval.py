import os
import sys
from operator import itemgetter
from typing import Optional, List
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.vectorstores import FAISS
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import CustomException
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self, session_id=None, retriever=None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.llm = self._load_llm()
            self.contextaualize_question = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.context_qa = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            # if retriever is None:
                # raise ValueError("Retriever is not provided.")
            self.retriever = retriever
            if self.retriever is not None:
                self._build_lcel_chain()
            # self._build_lcel_chain()
            self.log.info(f"ConversationalRAG initialized with context and history aware retriever.")

        except Exception as e:
            self.log.error(f"Error initializing ConversationalRAG: {str(e)}")
            raise CustomException(f"Failed to initialize ConversationalRAG:", sys)
                
    def load_retriever_from_faiss(self, index_path: str):
        try:
            embeddings = ModelLoader().load_embeddings()

            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS Index directory not found at: {index_path}")
            
            vectorestore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            self.retriever = vectorestore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self._build_lcel_chain()
            self.log.info("Retriever loaded from FAISS.")
            return self.retriever
        
        except Exception as e:
            self.log.error(f"Error loading retreiver: {str(e)}")
            raise CustomException(f"Failed to load retreiver:", sys)

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("Failed to load LLM model.")
            self.log.info("LLM loaded.")
            return llm

        except Exception as e:
            self.log.error(f"Error Loading LLM: {str(e)}")
            raise CustomException(f"Failed to load LLM model:", sys)  
    
    def invoke(self, user_input: str, chat_history : Optional[List[str]]=None):
        try:
            chat_history = chat_history or []
            payload = {"input": user_input, "chat_history": chat_history}
            response = self.chain.invoke(payload)
            if not response:
                self.log.warning("No answer found in response.")
                return "No answer found in response."
            
            self.log.info(f"Chain Invoked Successfully.", session_id=self.session_id, user_input=user_input, answer_preview=response[:150])
            return response
        except Exception as e:
            self.log.error(f"Error invoking ConversationalRAG: {str(e)}")
            raise CustomException(f"Failed to invoke ConversationalRAG:", sys)
    
    @staticmethod    
    def _format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])
    
    def _build_lcel_chain(self):
        try:
            question_retriever = (
                {
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history")}
                |self.contextaualize_question
                |self.llm
                |StrOutputParser()
            )

            retrieve_docs = question_retriever | self.retriever | self._format_docs
            self.chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history"),
                }
                |self.context_qa
                |self.llm
                |StrOutputParser()
            )
            self.log.info("LCEL chain built.")

        except Exception as e:
            self.log.error(f"Error building LCEL chain: {str(e)}")
            raise CustomException(f"Failed to build LCEL chain:", sys)