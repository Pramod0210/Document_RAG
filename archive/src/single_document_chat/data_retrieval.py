import os
import sys
import fitz
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
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
            self.retriever = retriever
            self.llm = self._load_llm()
            self.contextaualize_question = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.context_qa = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            self.history_aware_retriever = create_history_aware_retriever(self.llm, self.retriever, self.contextaualize_question)
            self.log.info(f"ConversationalRAG initialized with context and history aware retriever.")

            self.qa_chain = create_stuff_documents_chain(self.llm, self.context_qa)
            self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.qa_chain)
            self.log.info(f"ConversationalRAG initialized with RAG chain.", session_id=session_id)
            self.chain = RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="output"

            )

            self.log.info(f"ConversationalRAG initialized with RunnableWithMessageHistory.", session_id=session_id)

        except Exception as e:
            self.log.error(f"Error initializing ConversationalRAG: {str(e)}")
            raise CustomException(f"Failed to initialize ConversationalRAG:", sys)
        

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            self.log.info("LLM loaded.")
            return llm

        except Exception as e:
            self.log.error(f"Error Loading LLM: {str(e)}")
            raise CustomException(f"Failed to load LLM model:", sys)

    def _get_session_history(self, session_id):
        try:
            return ChatMessageHistory(session_id=session_id)
        except Exception as e:
            self.log.error(f"Failed to load session history: {str(e)}")
            raise CustomException(f"Failed to load session history:", sys)


    def load_retriever_from_faiss(self, index_path: str):
        try:
            embeddings = ModelLoader().load_embeddings()

            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS Index directory not found at: {index_path}")
            
            vectorestore = FAISS.load_local(index_path, embeddings)
            retriever = vectorestore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self.log.info("Retriever loaded from FAISS.")
            return retriever
        
        except Exception as e:
            self.log.error(f"Error loading retreiver: {str(e)}")
            raise CustomException(f"Failed to load retreiver:", sys)

    def invoke(self, user_input: str):
        try:
            response = self.chain.invoke(
                {"input": user_input},
                config = {"configurable":{"session_id": self.session_id}})
            answer = response.get("answer", "No answer")
            if not answer:
                self.log.warning("No answer found in response.", session_id=self.session_id)

            self.log.info(f"Chain Invoked Successfully.", session_id=self.session_id, user_input=user_input, answer_preview=answer[:150])
            return answer
        except Exception as e:
            self.log.error(f"Error invoking: {str(e)}")
            raise CustomException(f"Failed to invoke:", sys)

